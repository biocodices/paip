import luigi

from paip.task_types import SampleTask
from paip.pipeline import AddOrReplaceReadGroups, CreateRealignmentIntervals


class RealignAroundIndels(SampleTask):
    """
    Expects a BAM file and an intervals file. Runs a command to realign the reads
    in those intervals and produce a new BAM file with the fixed alignments.
    """
    def requires(self):
        return [AddOrReplaceReadGroups(sample=self.sample),
                CreateRealignmentIntervals(sample=self.sample)]

    def run(self):

        with self.output().temporary_path() as self.temp_bam:
            program_name = 'gatk IndelRealigner'
            program_options = {
                'input_bam': self.input()[0].fn,
                'targets_file': self.input()[1].fn,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_bai()

    def output(self):
        filename = self.sample_path('realignment.bam')
        return luigi.LocalTarget(filename)

