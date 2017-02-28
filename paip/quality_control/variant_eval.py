from paip.variant_calling import FilterGenotypes
from paip.task_types import CohortTask


class VariantEval(CohortTask):
    """
    Takes a VCF and creates a stats file of its variants using GATK's VariantEval.
    """
    REQUIRES = FilterGenotypes
    OUTPUT = 'eval.grp'

    def run(self):
        with self.output().temporary_path() as temp_outfile:
            program_name = 'gatk VariantEval'
            program_options = {
                'input_vcf': self.input().fn,
                'output_file': temp_outfile,
            }
            self.run_program(program_name, program_options)

