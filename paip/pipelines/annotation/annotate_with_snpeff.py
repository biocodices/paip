from paip.task_types import CohortTask
from paip.pipelines.annotation import AnnotateWithVep


class AnnotateWithSnpeff(CohortTask):
    """
    Takes a VCF and adds SnpEff annotations. Generats a new VCF.
    """
    REQUIRES = AnnotateWithVep
    OUTPUT_RENAMING = ('.vcf.gz', '.eff.vcf')

    def run(self):
        with self.output().temporary_path() as temp_vcf:
            program_name = 'snpeff annotate'
            program_options = {
                'input_vcf': self.input().path,
                'output_summary_csv': self.path('snpEff.summary.csv'),
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf)

    @property
    def genes_txt(self):
        return self.path('snpEff.summary.genes.txt')
