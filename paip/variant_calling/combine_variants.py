import luigi

from paip.task_types import CohortTask
from paip.variant_calling import FilterSNPs, FilterIndels


class CombineVariants(CohortTask):
    """
    Takes a VCF of SNPs and a VCF of Indels, and merges them in a single VCF.
    """
    REQUIRES = [FilterSNPs, FilterIndels]

    def run(self):
        input_snps = self.input()[0].fn
        input_indels = self.input()[1].fn

        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk CombineVariants snps_indels'
            program_options = {
                'input_snps': input_snps,
                'input_indels': input_indels,
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        return luigi.LocalTarget(self.cohort_path('filt.vcf'))

