import luigi

from paip.task_types import SampleTask
from paip.pipeline import RealignAroundIndels


class CreateRecalibrationTable(SampleTask):
    """
    Expects a BAM file. Runs a command to create a plain text file with a table
    for the recalibration of the scores of each called base. The recalibration
    of scores is needed because of the previous realignment.
    """
    def requires(self):
        return RealignAroundIndels(self.sample)

    def run(self):

        with self.output().temporary_path() as self.temp_output_path:
            program_options = {
                'input_bam': self.input().fn,
                'outfile': self.temp_output_path,
            }

            self.run_program('gatk BaseRecalibrator', program_options)

    def output(self):
        filename = self.sample_path('recalibration_table')
        return luigi.LocalTarget(filename)
