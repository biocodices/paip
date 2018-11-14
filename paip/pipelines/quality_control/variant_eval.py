from paip.pipelines.variant_calling import KeepReportableGenotypes
from paip.task_types import SampleTask


class VariantEval(SampleTask):
    """
    Takes a VCF and creates a stats file of its variants using GATK's
    VariantEval.
    """
    REQUIRES = KeepReportableGenotypes
    OUTPUT = 'eval.grp'

    def run(self):
        with self.output().temporary_path() as temp_outfile:
            program_name = 'gatk VariantEval'
            program_options = {
                'input_vcf': self.input().path,
                'output_file': temp_outfile,
            }
            self.run_program(program_name, program_options)

