from paip.task_types import SampleTask
from paip.pipelines.variant_calling import CompressAlignment


class AddOrReplaceReadGroups(SampleTask):
    """
    Expects a SAM file with aligned reads. Reads sequencing data from the
    working directory and runs a command that adds (or replaces) read groups
    to each read. The result is written to a BAM file.
    """
    REQUIRES = CompressAlignment
    OUTPUT = 'raw_alignment_with_read_groups.bam'

    def run(self):
        with self.output().temporary_path() as self.temp_bam:
            program_name = 'picard AddOrReplaceReadGroups'
            program_options = {
                'input_bam': self.input().path,
                'library_id': self.library_id,
                'platform': self.platform,
                'flowcell_id': self.flowcell_id,
                'lane_number': self.lane_number,
                'sample_id': self.sample,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_bai()

