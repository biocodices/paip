from paip.pipelines.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask


class SamtoolsBedcov(SampleTask):
    """
    Takes a BAM and creates coverage statistics samtools bedcov.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'samtools_bedcov'

    def run(self):
        program_name = 'samtools bedcov'
        program_options = {
            'input_bam': self.input().fn,
        }

        stdout, _ = self.run_program(program_name, program_options,
                                     log_stdout=False)

        with open(self.output().fn, 'wb') as f:
            f.write(stdout)


