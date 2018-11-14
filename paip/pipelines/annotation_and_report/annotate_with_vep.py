from paip.task_types import CohortTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateWithVEP(CohortTask):
    """
    Takes a VCF and adds Variant Effect Predictor annotations.
    Generats a new VCF.
    """
    REQUIRES = FilterGenotypes
    OUTPUT = 'vep.tsv'

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'vep annotate'
            program_options = {
                'input_vcf': self.input().path,
                'output_vcf': self.temp_vcf,
                'output_stats_html': self.output().path.replace('.tsv',
                                                                '_summary.html')
            }
            self.run_program(program_name, program_options)

