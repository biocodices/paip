import luigi

from paip.task_types import CohortTask
from paip.pipeline import CombineVariants


class FilterSNPs(CohortTask):
    """
    Takes a VCF and applies filters to each genotype. Generates a new VCF.
    """
    REQUIRES = CombineVariants

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk VariantFiltration snps'
            program_options = {
                'input_vcf': self.input().fn,
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        fn = self.input().fn.replace('.vcf', '.geno_filtered.vcf')
        return luigi.LocalTarget(fn)

