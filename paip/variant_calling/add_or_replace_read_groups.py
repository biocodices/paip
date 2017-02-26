from paip.task_types import SampleTask
from paip.variant_calling import AlignToReference


class AddOrReplaceReadGroups(SampleTask):
    """
    Expects a SAM file with aligned reads. Reads sequencing data from the
    working directory and runs a command that adds (or replaces) read groups
    to each read. The result is written to a BAM file.
    """
    REQUIRES = AlignToReference
    OUTPUT = 'raw_alignment_with_read_groups.bam'

    def run(self):
        with self.output().temporary_path() as self.temp_bam:
            program_name = 'picard AddOrReplaceReadGroups'
            program_options = {
                'input_sam': self.input().fn,
                'sample_id': self.id_in_sequencing,
                'library_id': self.library_id,
                'sequencing_id': self.sequencing_id,
                'platform_unit': self.platform_unit,
                'platform': self.platform,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_bai()
