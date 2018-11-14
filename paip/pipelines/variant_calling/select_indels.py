from paip.task_types import CohortTask
from paip.pipelines.variant_calling import MergeVCFs, JointGenotyping


class SelectIndels(CohortTask):
    """
    Take a cohort VCF and produce a new VCF keeping only the SNPs.

    This step is needed to later apply SNP-specific filters to the
    resulting VCF.
    """
    OUTPUT = 'indels.vcf'

    def requires(self):
        in_targets_pipeline = self.pipeline_type == 'target_sites'
        task = MergeVCFs if in_targets_pipeline else JointGenotyping

        return task(**self.param_kwargs)

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk SelectVariants indels'
            program_options = {
                'input_vcf': self.input().path,
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

