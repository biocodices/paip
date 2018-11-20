from paip.task_types import SampleTask
from paip.pipelines.variant_calling import (
    AddOrReplaceReadGroups,
    CreateRealignmentIntervals,
)


class RealignAroundIndels(SampleTask):
    """
    Expects a BAM file and an intervals file. Runs a command to realign the reads
    in those intervals and produce a new BAM file with the fixed alignments.
    """
    REQUIRES = [AddOrReplaceReadGroups, CreateRealignmentIntervals]
    OUTPUT = 'realignment.bam'

    def run(self):

        with self.output().temporary_path() as self.temp_bam:
            program_name = 'gatk3 IndelRealigner'
            program_options = {
                'input_bam': self.input()[0].path,
                'targets_file': self.input()[1].path,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_bai()

