import re
import logging

import pandas as pd

from paip.task_types import CohortTask
from paip.pipelines.annotation import AnnotateWithClinvarVcf


logger = logging.getLogger(__name__)


class AnnotateWithCosmic(CohortTask):
    """
    Takes a VCF and adds COSMIC IDs from COSMIC's VCF.
    Generats a new VCF.
    """
    REQUIRES = AnnotateWithClinvarVcf
    OUTPUT_RENAMING = ('.vcf', '.COS.vcf')

    def run(self):
        temp_vcf_1 = self.output().path.replace('.vcf', '-temp.vcf')
        program_name = 'snpsift COSMIC'
        program_options = {
            'input_vcf': self.input().path,
        }
        self.run_program(program_name, program_options,
                         redirect_stdout_to_path=temp_vcf_1)

        with self.output().temporary_path() as temp_vcf_2:
            self.add_COSMIC_INFO(temp_vcf_1,
                                 temp_vcf_2,
                                 self.config.resources['cosmic_mutation_data'])


    def add_COSMIC_INFO(self, vcf, new_vcf, cosmic_data_file):
        '''
        Add COSMIC INFO to the VCF lines where a COSMIC ID is found.
        Write the result to a *new_vcf*.
        '''
        cosmic_df = self.read_COSMIC_mutation_info(path=cosmic_data_file)

        # Use any line to create the meta information for the VCF:
        cosmic_meta_line = self.matches_to_INFO(cosmic_df.loc[0:0])[0]

        new_lines = []

        logger.info(f'Reading and parsig: {vcf}')
        last_line_was_INFO = False
        with open(vcf) as f:
            for line in f:
                line = line.strip()
                this_line_is_INFO = line.startswith('##INFO')

                if last_line_was_INFO and not this_line_is_INFO:
                    new_lines.append(cosmic_meta_line + "\n")

                is_genotype = not line.startswith('#')
                if is_genotype:
                    fields = line.split("\t")
                    ids = fields[2].split(';')
                    cosmic_ids = [id_ for id_ in ids if re.search(r'^COSM\d+$', id_)]
                    matches = cosmic_df[cosmic_df['Mutation ID'].isin(cosmic_ids)]
                    if len(matches):
                        extra_info_chunk = self.matches_to_INFO(matches)[1]
                        fields[7] = fields[7] + extra_info_chunk
                        line = "\t".join(fields)

                new_lines.append(line + "\n")

                last_line_was_INFO = this_line_is_INFO

        logger.info(f'Writing to: {new_vcf}')
        with open(new_vcf, 'w') as f:
            for line in new_lines:
                f.write(line)

    def read_COSMIC_mutation_info(self, path):
        return pd.read_table(path)

    def matches_to_INFO(self, df):
        '''
        Transform one or more rows of data from a DataFrame *df* into a tuple
        of 2 strings: a meta line for the VCF and a chunk that can be put in
        the VCF INFO field.
        '''
        df = df.applymap(lambda value: value.replace(' ', '_') \
                         if isinstance(value, str) else value)

        fields = '|'.join(df.columns)
        meta_line = f'##INFO=<ID=COSMIC,Number=1,Type=String,Description="{fields}">'

        values = ['|'.join(str(v) for v in row.values)
                  for ix, row in df.iterrows()]
        merged_values = ','.join(values)
        info_chunk = f';COSMIC={merged_values}'

        return (meta_line, info_chunk)
