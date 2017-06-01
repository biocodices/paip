import jinja2
from vcf_to_dataframe import vcf_to_dataframe

from paip.helpers import available_resources


class IGVScriptHelper:
    """
    Helper class to write a batch script for IGV from the variants
    present in a VCF and a script template.
    """
    def __init__(self, vcf, template_path, template_data={}):
        """
        Provide:

        - a *vcf* with the variants to analyse in IGV,
        - a *template_path* to a template in jinja2 format,
        - the *template_data* (a dictionary) with the values to fill the
          variables in the template.

        Will write a script for IGV using the passed template and the
        passed data. Reads the VCF for variants and passes them as dicts
        under the 'variants' key, which can be included in the template.

        Each variant has 'chrom', 'pos', 'range_around', and 'dest_filename'
        as available keys to use in the template.

        When writing the script, the helper will complain if any variables
        in the template are not defined in the passed *template_data*.

        Usage:

          > igv_helper = IGVScriptHelper(
              vcf='/path/to/sample.vcf',
              template_path='/path/to/batch_script_template',
              template_data={
                  'template-variable-1': 'some-value',
                  'template-variable-2': 'some-other-value',
              }
          )
          > igv_helper.write_script(out_path='/path/to/out_script')

        """
        self.vcf = vcf
        self.template_data = template_data
        self.template_path = template_path

    def _read_template(self):
        """
        Read the contents of self.template.
        """
        with open(self.template_path) as f:
            template = f.read()

        return template

    def _read_variants_file(self):
        """
        Reads *self.vcf* and makes a dictionary with the variants,
        suited for use in the script template.
        """
        variants = vcf_to_dataframe(self.vcf)[['chrom', 'pos', 'id']]
        variants = variants.to_dict(orient='records')

        for variant in variants:
            window = 160  # Basepairs to show centered in the variant
            variant['range_around'] = 'chr{}:{}-{}'.format(
                variant['chrom'],
                variant['pos'] - window//2,
                variant['pos'] + window//2,
            )
            variant['dest_filename'] = \
                '{chrom}_{pos}_{id}.png'.format(**variant)

        return variants

    def _data_for_template(self):
        """
        Merge the available resources with the user-provided data
        located in self.template_data. Returns a dictionary.
        """
        data = available_resources()
        data.update(self.template_data)
        data['variants'] = self._read_variants_file()
        return data

    def write_script(self, out_path):
        """
        Writes the script to *out_path* with the data in self.template_data.
        """
        template_content = self._read_template()
        template_data = self._data_for_template()
        jinja_env = jinja2.Environment(undefined=jinja2.StrictUndefined,
                                       trim_blocks=True)
        template = jinja_env.from_string(template_content)
        script_content = template.render(**template_data)

        with open(out_path, 'w') as f:
            f.write(script_content)

