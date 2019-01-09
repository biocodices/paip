from paip.task_types import CohortTask
from paip.pipelines.annotation import AnnotateDbsnpId


class AnnotateGnomadFrequencies(CohortTask):
    """
    Take a VCF and add INFO data from a gnomAD VCF file. Do NOT add IDs.
    """
    REQUIRES = AnnotateDbsnpId
    OUTPUT_RENAMING = ('.vcf', '.AD.vcf')

    def run(self):
        with self.output().temporary_path() as temp_vcf:
            program_name = 'snpsift gnomAD'
            program_options = {
                'input_vcf': self.input().path,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf,
                             log_stdout=False)
