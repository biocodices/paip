import luigi

from paip.task_types import CohortTask
from paip.pipelines.variant_calling import CombineVariants


class FilterGenotypes(CohortTask):
    """
    Takes a VCF and applies filters to each genotype. Generates a new VCF.
    """
    REQUIRES = CombineVariants

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk3 VariantFiltration genos'
            program_options = {
                'input_vcf': self.input().path,
                'output_vcf': self.temp_vcf,
                'min_gq': self.min_gq,
                'min_dp': self.min_dp,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        fn = self.input().path.replace('.vcf', '.geno_filt.vcf')
        return luigi.LocalTarget(fn)

