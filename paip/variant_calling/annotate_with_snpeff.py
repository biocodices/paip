import luigi

from paip.task_types import SampleTask, CohortTask
from paip.variant_calling import VariantCallingReady


class AnnotateWithSnpeff(SampleTask):
    """
    Takes a VCF and adds SnpEff annotations. Generats a new VCF.
    """
    pipeline_type = luigi.Parameter()

    REQUIRES = VariantCallingReady

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'snpeff annotate'
            program_options = {
                'input_vcf': self.input().fn,
                'output_summary_csv': self.sample_path('snpEff.summary.csv'),
            }

            # Snpeff outputs the annotated VCF to STDOUT
            stdout, _ = self.run_program(program_name, program_options,
                                         log_stdout=False)

            with open(self.temp_vcf, 'wb') as f:
                f.write(stdout)

    def output(self):
        fn = self.input().fn.replace('.vcf', '.eff.vcf')
        return luigi.LocalTarget(fn)


class AnnotateWithSnpeffCohort(CohortTask):
    """
    Runs AnnotateWithSnpeff for all samples in a cohort.
    """
    def requires(self):
        for sample in self.sample_list:
            yield AnnotateWithSnpeff(sample=sample, basedir=self.basedir,
                                     pipeline_type=self.pipeline_type)

    def output(self):
        return [req.output() for req in self.requires()]

