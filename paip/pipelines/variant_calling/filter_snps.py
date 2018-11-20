import luigi

from paip.task_types import CohortTask
from paip.pipelines.variant_calling import SelectSNPs


class FilterSNPs(CohortTask):
    """
    Takes a VCF of SNPs and applies GATK's SNP-filters on them.

    Generates a new VCF.
    """
    REQUIRES = SelectSNPs

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk3 VariantFiltration snps'
            program_options = {
                'input_vcf': self.input().path,
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        fn = self.input().path.replace('.vcf', '.filt.vcf')
        return luigi.LocalTarget(fn)

