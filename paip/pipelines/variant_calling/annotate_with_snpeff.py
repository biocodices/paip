import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import KeepReportableGenotypes


class AnnotateWithSnpeff(SampleTask):
    """
    Takes a VCF and adds SnpEff annotations. Generats a new VCF.
    """
    REQUIRES = KeepReportableGenotypes

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'snpeff annotate'
            program_options = {
                'input_vcf': self.input().fn,
                'output_summary_csv': self.path('snpEff.summary.csv'),
            }

            # Snpeff outputs the annotated VCF to STDOUT
            stdout, _ = self.run_program(program_name, program_options,
                                         log_stdout=False)

            with open(self.temp_vcf, 'wb') as f:
                f.write(stdout)

    def output(self):
        fn = self.input().fn.replace('.vcf', '.eff.vcf')
        return luigi.LocalTarget(fn)

