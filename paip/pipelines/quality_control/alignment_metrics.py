from paip.task_types import SampleTask
from paip.pipelines.variant_calling import RecalibrateAlignmentScores


class AlignmentMetrics(SampleTask):
    """
    Expects a BAM file. Runs Picard tools to generate alignment metrics.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'alignment_metrics.txt'

    def run(self):
        with self.output().temporary_path() as temp_output:
            program_name = 'picard CollectAlignmentSummaryMetrics'
            program_options = {
                'input_bam': self.input().path,
                'output_txt': temp_output,
            }
            self.run_program(program_name, program_options)

