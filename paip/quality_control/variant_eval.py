import luigi

from paip.variant_calling import VariantCallingReady
from paip.task_types import SampleTask, CohortTask


class VariantEval(SampleTask):
    """
    Takes a VCF and creates a stats file of its variants using GATK's VariantEval.
    """
    REQUIRES = VariantCallingReady
    OUTPUT = 'eval.grp'

    pipeline_type = luigi.Parameter()

    def run(self):
        with self.output().temporary_path() as temp_outfile:
            program_name = 'gatk VariantEval'
            program_options = {
                'input_vcf': self.input().fn,
                'output_file': temp_outfile,
            }
            self.run_program(program_name, program_options)


class VariantEvalCohort(CohortTask):
    """
    Runs VariantEval for all sample in the cohort.
    """
    def requires(self):
        for sample in self.sample_list:
            yield VariantEval(sample=sample,
                              basedir=self.basedir,
                              pipeline_type=self.pipeline_type)

    def output(self):
        return [req.output() for req in self.requires()]

