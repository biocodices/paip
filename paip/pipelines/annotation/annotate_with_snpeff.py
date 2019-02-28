import luigi

from paip.task_types import CohortTask
from paip.pipelines.annotation import AnnotateWithVep


class AnnotateWithSnpeff(CohortTask):
    """
    Takes a VCF and adds SnpEff annotations. Generats a new VCF.
    """
    REQUIRES = AnnotateWithVep

    def output(self):
        # NOTE: input is gzipped, but output is NOT gzipped!
        vcf = self.input().path.replace('.vcf.gz', '.eff.vcf')
        summary = self.path('snpEff.summary.genes.txt')
        genes = self.path('snpEff.summary.genes.txt')
        return {
            'summary': luigi.LocalTarget(summary),
            'vcf': luigi.LocalTarget(vcf),
            'genes': luigi.LocalTarget(genes),
        }

    def run(self):
        with self.output()['vcf'].temporary_path() as temp_vcf:
            program_name = 'snpeff annotate'
            program_options = {
                'input_vcf': self.input().path,
                'output_summary_csv': self.path('snpEff.summary.csv'),
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf)
