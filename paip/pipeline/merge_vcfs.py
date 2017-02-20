import luigi

from paip.task_types import CohortTask
from paip.pipeline import CallTargets


class MergeVcfs(CohortTask):
    """
    Take the single-sample VCF files from each sample in the target-sites
    pipeline and merge them into a multi-sample VCF.
    """
    def requires(self):
        return [CallTargets(sample) for sample in self.sample_list]

    def run(self):
        input_vcfs_params = ['--variant {}'.format(input_vcf.fn)
                             for input_vcf in self.input()]

        with self.output().temporary_path() as self.temp_output_path:
            program_name = 'gatk CombineVariants target_sites'
            program_options = {
                'input_vcfs': ' '.join(input_vcfs_params),
                'output_vcf': self.temp_output_path,
            }

            self.run_program(program_name, program_options)

    def output(self):
        fn = 'target_sites.raw.vcf'
        return luigi.LocalTarget(self.cohort_path(fn))

