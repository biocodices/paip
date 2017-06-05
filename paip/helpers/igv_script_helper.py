from copy import deepcopy
import json

import jinja2
from vcf_to_dataframe import vcf_to_dataframe

from paip.helpers import available_resources


class IGVScriptHelper:
    """
    Helper class to write a batch script for IGV from the variants
    present in a VCF and a script template.
    """
    def __init__(self, template_path, vcf=None, variants_json=None,
                 template_data={}):
        """
        Provide:

        - a *template_path* to a template in jinja2 format,
        - a *vcf* with the variants to analyse in IGV, or a *variants_json*
          with the path to a json file that has the list of variants to
          include (their ID will be looked in 'vcf_id'),
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
        self.variants_file = vcf or variants_json

        if not self.variants_file:
            raise ValueError('Please provide either a VCF or a JSON '
                             'with the variants that shoud be analysed.')

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
        Reads *self.variants_file* and makes a dictionary with the variants,
        adding some fields to use in the script template. The file might be a
        VCF or a JSON with a list of variants.
        """
        if self.variants_file.endswith('.vcf'):
            read_function = self._read_variants_from_vcf
        elif self.variants_file.endswith('.json'):
            read_function = self._read_variants_from_json
        else:
            raise ValueError("I don't know how to read {}"
                             .format(self.variants_file))

        variants = read_function(self.variants_file)
        return self._add_fields_to_variants(variants)

    @staticmethod
    def _read_variants_from_json(variants_json):
        """
        Read variants from a *json*, and return them as a dictionary.

        Any keys with a "vcf_" prefix will be copied to a new key without
        that prefix.
        """
        with open(variants_json) as f:
            variants = json.load(f)

        for variant in variants:
            for key in list(variant.keys()):
                new_key = key.replace('vcf_', '')
                variant[new_key] = variant[key]

        return variants

    @staticmethod
    def _read_variants_from_vcf(vcf):
        """
        Read variants from a *vcf* path, and return them as a dictionary.
        """
        variants = vcf_to_dataframe(vcf)[['chrom', 'pos', 'id']]
        variants = variants.to_dict(orient='records')

        return variants

    @staticmethod
    def _add_fields_to_variants(variants, window=40):
        """
        From a list of variants (each one a dict), adds 'range_around' and
        'dest_filename' to each one based on their 'chrom', 'pos', and 'id'.

        You can set the *window* around each variant that will be used to
        define the 'range_around' it.

        Returns a copy of the variants modified in this way.
        """
        variants = deepcopy(variants)

        for variant in variants:
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

