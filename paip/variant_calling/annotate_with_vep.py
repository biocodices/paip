import luigi

from paip.task_types import CohortTask
from paip.variant_calling import FilterGenotypes


class AnnotateWithVEP(CohortTask):
    """
    Takes a VCF and adds Variant Effect Predictor annotations.
    Generats a new VCF.
    """
    REQUIRES = FilterGenotypes

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'vep annotate'
            program_options = {
                'input_vcf': self.input().fn,
                'output_vcf': self.temp_vcf,
            }
            self.run_program(program_name, program_options)

    def output(self):
        fn = self.cohort_path('vep.tsv')
        return luigi.LocalTarget(fn)
