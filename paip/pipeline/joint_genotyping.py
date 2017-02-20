import luigi

from paip.task_types import CohortTask
from paip.pipeline import CallVariants


class JointGenotyping(CohortTask):
    """
    Use the gVCF files from many samples to do a joint genotyping.
    Generates a multisample VCF.
    """
    def requires(self):
        return [CallVariants(sample) for sample in self.sample_list]

    def run(self):
        input_gvcfs_params = ['--variant {}'.format(input_gvcf.fn)
                              for input_gvcf in self.input()]

        with self.output().temporary_path() as self.temp_output_path:
            program_name = 'gatk GenotypeGVCFs'
            program_options = {
                'input_gvcfs': ' '.join(input_gvcfs_params),
                'output_vcf': self.temp_output_path
            }

            self.run_program(program_name, program_options)

        self.rename_extra_temp_output_file('.idx')

    def output(self):
        fn = 'all_sites.vcf'
        return luigi.LocalTarget(self.cohort_path(fn))

