from paip.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask, CohortTask


class SamtoolsStats(SampleTask):
    """
    Takes a BAM and creates a stats file of its variants using samtools stats.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'samtools_stats'

    def run(self):
        program_name = 'samtools stats'
        program_options = {
            'input_bam': self.input().fn,
        }

        stdout, _ = self.run_program(program_name, program_options,
                                     log_stdout=False)

        with open(self.output().fn, 'wb') as f:
            f.write(stdout)


class SamtoolsStatsCohort(CohortTask):
    """
    Runs SamtoolsStats for all sample in the cohort.
    """
    def requires(self):
        for sample in self.sample_list:
            yield SamtoolsStats(sample=sample,
                                basedir=self.basedir)

    def output(self):
        return [req.output() for req in self.requires()]

