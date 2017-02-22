import luigi

from paip.task_types import CohortTask
from paip.pipeline import MakeGVCF


class JointGenotyping(CohortTask):
    """
    Use the gVCF files from many samples to do a joint genotyping.
    Generates a multisample VCF.
    """
    def requires(self):
        return [MakeGVCF(sample=sample, pipeline_type=self.pipeline_type)
                for sample in self.sample_list]

    def run(self):
        # MakeGVCF outputs both a GVCF and a BAM (in that order).
        # We use the GVCFs here:
        input_gvcfs = [outputs[0] for outputs in self.input()]
        input_gvcfs_params = ['--variant {}'.format(input_gvcf.fn)
                              for input_gvcf in input_gvcfs]

        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk GenotypeGVCFs ' + self.pipeline_type
            program_options = {
                'input_gvcfs': ' '.join(input_gvcfs_params),
                'output_vcf': self.temp_vcf
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        fn = self.cohort_path(self.pipeline_type + '.vcf')
        return luigi.LocalTarget(fn)

