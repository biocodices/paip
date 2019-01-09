from paip.task_types import CohortTask
from paip.pipelines.annotation import AnnotateWithSnpeff


class AnnotateWithClinvarVcf(CohortTask):
    """
    Takes a VCF and adds ClinVar annotations from ClinVar's VCF.
    Generats a new VCF.
    """
    REQUIRES = AnnotateWithSnpeff
    OUTPUT_RENAMING = ('.vcf', '.clin.vcf')

    def run(self):
        with self.output().temporary_path() as temp_vcf:
            program_name = 'snpsift ClinVar'
            program_options = {
                'input_vcf': self.input().path,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf)
