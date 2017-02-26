import luigi

from paip.task_types import CohortTask
from paip.variant_calling import AnnotateWithDbSNP


class SelectIndels(CohortTask):
    """
    Take a cohort VCF and produce a new VCF keeping only the SNPs.

    This step is needed to later apply SNP-specific filters to the
    resulting VCF.
    """
    REQUIRES = AnnotateWithDbSNP

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk SelectVariants indels'
            program_options = {
                'input_vcf': self.input().fn,
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        return luigi.LocalTarget(self.cohort_path('indels.vcf'))

