from paip.task_types import SampleTask
from paip.pipelines.variant_calling import AddOrReplaceReadGroups


class CreateRealignmentIntervals(SampleTask):
    """
    Expects a BAM file with mapped reads and runs a command to create an
    'intervals' file with the regions that should be realigned considering
    known human indels.
    """
    REQUIRES = AddOrReplaceReadGroups
    OUTPUT = 'realignment.intervals'

    def run(self):

        with self.output().temporary_path() as temp_out:
            program_name = 'gatk RealignerTargetCreator'
            program_options = {
                'input_bam': self.input().path,
                'outfile': temp_out,
            }

            self.run_program(program_name, program_options)

