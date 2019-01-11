from paip.task_types import CohortTask
from paip.pipelines.annotation import AnnotateWithClinvarVcf


class AnnotateWithCosmic(CohortTask):
    """
    Takes a VCF and adds COSMIC IDs from COSMIC's VCF.
    Generats a new VCF.
    """
    REQUIRES = AnnotateWithClinvarVcf
    OUTPUT_RENAMING = ('.vcf', '.COS.vcf')

    def run(self):
        with self.output().temporary_path() as temp_vcf:
            program_name = 'snpsift COSMIC'
            program_options = {
                'input_vcf': self.input().path,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf)
