from paip.task_types import CohortTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateWithVep(CohortTask):
    """
    Takes a VCF and adds Variant Effect Predictor annotations.
    Generats a new VCF.
    """
    REQUIRES = FilterGenotypes
    OUTPUT_RENAMING = ('.vcf', '.vep.vcf.gz')

    def run(self):
        with self.output().temporary_path() as self.temp_tsv:
            program_name = 'vep annotate'
            program_options = {
                'input_vcf': self.input().path,
                'output_tsv': self.temp_tsv,
                'stats_file': self.output().path.replace('.vcf.gz',
                                                         '.summary.html'),
                'warning_file': self.output().path.replace('.vcf.gz',
                                                           '.warning.txt')
            }
            self.run_program(program_name, program_options)
