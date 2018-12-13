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
        with self.output().temporary_path() as self.temp_tsv:
            program_name = 'vep annotate'
            program_options = {
                'input_vcf': self.input().path,
                'output_tsv': self.temp_tsv,
                'output_stats_html': self.output().path.replace('.tsv',
                                                                '_summary.html')
            }
            self.run_program(program_name, program_options)
