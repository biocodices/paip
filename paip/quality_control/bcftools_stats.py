import luigi

from paip.variant_calling import VariantCallingReady
from paip.task_types import SampleTask, CohortTask


class BcftoolsStats(SampleTask):
    """
    Takes a VCF and creates a stats file of its variants using bcftools stats.
    """
    REQUIRES = VariantCallingReady
    OUTPUT = 'bcftools_stats'

    pipeline_type = luigi.Parameter()

    def run(self):
        program_name = 'bcftools stats'
        program_options = {
            'input_vcf': self.input().fn,
        }

        stdout, _ = self.run_program(program_name, program_options,
                                     log_stdout=False)

        with open(self.output().fn, 'wb') as f:
            f.write(stdout)


class BcftoolsStatsCohort(CohortTask):
    """
    Runs BcftoolsStats for all sample in the cohort.
    """
    def requires(self):
        for sample in self.sample_list:
            yield BcftoolsStats(sample=sample,
                                basedir=self.basedir,
                                pipeline_type=self.pipeline_type)

    def output(self):
        return [req.output() for req in self.requires()]

