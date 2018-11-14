from paip.pipelines.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask
from paip.helpers.create_cohort_task import create_cohort_task


class SamtoolsDepth(SampleTask):
    """
    Takes a BAM and creates coverage statistics with samtools depth.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'samtools_depth'

    def run(self):
        program_name = 'samtools depth'
        program_options = {
            'input_bam': self.input().path,
        }
        self.run_program(program_name, program_options,
                         redirect_stdout_to_path=self.output().path)


SamtoolsDepthCohort = create_cohort_task(SamtoolsDepth)
