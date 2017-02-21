import luigi

from paip.task_types import CohortTask
from paip.pipeline import CallTargets


class MergeVCFs(CohortTask):
    """
    Take the single-sample VCF files from each sample in the target_sites
    pipeline and merge them into a multi-sample VCF.
    """
    def requires(self):
        return [CallTargets(sample=sample, pipeline_type=self.pipeline_type)
                for sample in self.sample_list]

    def run(self):
        input_vcfs_params = ['--variant {}'.format(input_vcf.fn)
                             for input_vcf in self.input()]

        with self.output().temporary_path() as self.temp_output_path:
            program_name = 'gatk CombineVariants ' + self.pipeline_type
            program_options = {
                'input_vcfs': ' '.join(input_vcfs_params),
                'output_vcf': self.temp_output_path,
            }

            self.run_program(program_name, program_options)

        self.rename_extra_temp_output_file('.idx')

    def output(self):
        fn = self.cohort_path(self.pipeline_type + '.vcf')
        return luigi.LocalTarget(fn)

