from os import environ

import luigi

from paip.task_types import SampleTask
from paip.pipeline import RecalibrateScores


class CallVariants(SampleTask):
    """
    Expects a BAM file. Runs GATK's HaplotypeCaller to discover non-REF
    variant sites in the sample. The discovery is limited to the
    panel_regions.
    """
    def requires(self):
        return RecalibrateScores(self.sample)

    def run(self):

        with self.output().temporary_path() as self.temp_output_path:
            program_options = {
                'input_bam': self.input().fn,
                'output_vcf': self.temp_output_path,
            }

            program_name = 'gatk HaplotypeCaller variant_sites'
            program_name += ' for_exomes' if bool(environ.get('EXOME')) else ''
            self.run_program(program_name, program_options)

        self.rename_extra_temp_output_file('.idx')

    def output(self):
        fn = self.sample_path('raw_variants.gvcf')
        return luigi.LocalTarget(fn)

