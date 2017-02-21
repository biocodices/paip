import luigi

from paip.task_types import SampleTask
from paip.pipeline import AddOrReplaceReadGroups


class CreateRealignmentIntervals(SampleTask):
    """
    Expects a BAM file with mapped reads and runs a command to create an
    'intervals' file with the regions that should be realigned considering
    known human indels.
    """
    def requires(self):
        return AddOrReplaceReadGroups(sample=self.sample)

    def run(self):

        with self.output().temporary_path() as self.temp_output_path:
            program_options = {
                'input_bam': self.input().fn,
                'outfile': self.temp_output_path,
            }

            self.run_program('gatk RealignerTargetCreator', program_options)

    def output(self):
        filename = self.sample_path('realignment.intervals')
        return luigi.LocalTarget(filename)

