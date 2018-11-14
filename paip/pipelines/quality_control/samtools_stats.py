from paip.pipelines.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask


class SamtoolsStats(SampleTask):
    """
    Takes a BAM and creates a stats file of its variants using samtools stats.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'samtools_stats'

    def run(self):
        program_name = 'samtools stats'
        program_options = {
            'input_bam': self.input().path,
        }
        self.run_program(program_name, program_options,
                         redirect_stdout_to_path=self.output().path)
