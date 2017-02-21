from os import environ

import luigi

from paip.task_types import SampleTask
from paip.pipeline import RecalibrateScores


class CallTargets(SampleTask):
    """
    Expects a BAM file. Runs GATK's HaplotypeCaller to call the genotypes
    of the variants specified in a panel_variants VCF.
    """
    def requires(self):
        return RecalibrateScores(sample=self.sample)

    def run(self):

        with self.output().temporary_path() as self.temp_output_path:
            program_options = {
                'input_bam': self.input().fn,
                'output_vcf': self.temp_output_path,
            }

            program_name = 'gatk HaplotypeCaller target_sites'
            program_name += ' for_exomes' if bool(environ.get('EXOME')) else ''
            self.run_program(program_name, program_options)

        self.rename_extra_temp_output_file('.idx')

    def output(self):
        fn = self.sample_path('raw_targets.vcf')
        return luigi.LocalTarget(fn)

