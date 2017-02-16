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
        input_gvcfs_params = ['--variant {}'.format(infile.fn)
                              for infile in self.input()]
        input_gvcfs_param_string = ' '.join(input_gvcfs_params)

        with self.output().temporary_path() as self.temp_output_path:
            program_options = {
                'input_gvcfs_param_string': input_gvcfs_param_string,
                'output_vcf': self.temp_output_path
            }

            self.run_program('gatk GenotypeGVCFs', program_options)

        self.rename_extra_temp_output_file('.idx')

    def output(self):
        return luigi.LocalTarget(self.cohort_path('raw_genotypes.vcf'))

