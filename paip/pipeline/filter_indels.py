import luigi

from paip.task_types import CohortTask
from paip.pipeline import SelectIndels


class FilterIndels(CohortTask):
    """
    Takes a VCF of Indels and applies GATK's Indel-filters on them.

    Generates a new VCF.
    """
    REQUIRES = SelectIndels

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk VariantFiltration indels'
            program_options = {
                'input_vcf': self.input().fn,
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        fn = self.input().fn.replace('.vcf', '.filt.vcf')
        return luigi.LocalTarget(fn)


