import luigi

from paip.task_types import CohortTask
from paip.pipeline import CallTargets


class MergeVCFs(CohortTask):
    """
    Take the single-sample VCF files from each sample in the target_sites
    pipeline and merge them into a multi-sample VCF.
    """
    def requires(self):
        return [CallTargets(sample=sample) for sample in self.sample_list]

    def run(self):
        input_vcfs_params = ['--variant {}'.format(input_vcf.fn)
                             for input_vcf in self.input()]

        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk CombineVariants'
            program_options = {
                'input_vcfs': ' '.join(input_vcfs_params),
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        fn = self.cohort_path(self.pipeline_type + '.vcf')
        return luigi.LocalTarget(fn)

