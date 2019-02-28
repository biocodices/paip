import luigi

from paip.task_types import CohortTask
from paip.pipelines.annotation import AnnotateWithSnpeff


class AnnotateWithClinvarVcf(CohortTask):
    """
    Takes a VCF and adds ClinVar annotations from ClinVar's VCF.
    Generats a new VCF.
    """
    REQUIRES = AnnotateWithSnpeff

    # OUTPUT_RENAMING = ('.vcf', '.clin.vcf')
    def output(self):
        vcf = self.input()['vcf'].path.replace('.vcf', '.clin.vcf')
        return luigi.LocalTarget(vcf)

    def run(self):
        with self.output().temporary_path() as temp_vcf:
            program_name = 'snpsift ClinVar'
            program_options = {
                'input_vcf': self.input()['vcf'].path,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf)
