from paip.task_types import SampleTask
from paip.pipelines.annotation.annotate_with_clinvar_vcf import \
    AnnotateWithClinvarVcf
from paip.helpers.create_cohort_task import create_cohort_task


class ExtractSample(SampleTask):
    """
    Takes a multi-sample VCF and generates a new VCF keeping the
    genotypes of one sample.
    """
    OUTPUT = 'with_filters.vcf'

    def requires(self):
        params = self.param_kwargs.copy()
        # 'sample' parameter is not used by CohortTasks upstream:
        del(params['sample'])
        return AnnotateWithClinvarVcf(**params)

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk3 SelectVariants sample'
            program_options = {
                'input_vcf': self.input().path,
                'sample_id': self.sample,
                'output_vcf': self.temp_vcf,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=self.temp_vcf)

        # No longer used since GATK writes to STDOUT in this task:
        # self.rename_temp_idx()


ExtractSampleCohort = create_cohort_task(ExtractSample)
