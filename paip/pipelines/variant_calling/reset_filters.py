from paip.task_types import SampleTask
from paip.pipelines.variant_calling import CallTargets
from paip.helpers.create_cohort_task import create_cohort_task


class ResetFilters(SampleTask):
    """
    Expects a BAM file. Runs GATK's HaplotypeCaller to call the genotypes
    of the variants specified in a panel_variants VCF.
    """
    REQUIRES = CallTargets
    OUTPUT = 'no_filters.vcf'

    def run(self):
        # CallTargets outputs a VCF and a BAM, but we only need the VCF:
        input_vcf, _ = self.input()

        program_name = 'bcftools reset_filters'
        program_options = {
            'input_vcf': input_vcf.path,
            'output_vcf': self.output().path,
        }

        self.run_program(program_name, program_options)


ResetFiltersCohort = create_cohort_task(ResetFilters)

