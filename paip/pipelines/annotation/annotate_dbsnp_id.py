from paip.task_types import CohortTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateDbsnpId(CohortTask):
    """
    Take a VCF and add IDs from a dbSNP VCF file.

    TODO: Replace any previous ID in the VCF, leaving only the preferred
    DbSNP's version. (Not implemented yet.)
    """
    REQUIRES = FilterGenotypes
    OUTPUT_RENAMING = ('.vcf', '.dbSNP.vcf')

    def run(self):
        with self.output().temporary_path() as temp_vcf:
            program_name = 'snpsift dbSNP'
            program_options = {
                'input_vcf': self.input().path,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf,
                             log_stdout=False)
