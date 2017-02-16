import luigi

from paip.task_types import SampleTask
from paip.pipeline import AlignToReference


class AddOrReplaceReadGroups(SampleTask):
    """
    Expects a SAM file with aligned reads. Reads sequencing data from the
    working directory and runs a command that adds (or replaces) read groups
    to each read. The result is written to a BAM file.
    """
    def requires(self):
        return AlignToReference(self.sample)

    def run(self):
        # This step assumes that the pipeline is run from the *parent*
        # directory of the sample dir, where sequencing_data.yml will
        # be located:
        self.load_sample_data_from_yaml('sequencing_data.yml')

        with self.output().temporary_path() as self.temp_output_path:
            program_options = {
                'input_sam': self.input().fn,
                'sample_id': self.id_in_sequencing,
                'library_id': self.library_id,
                'sequencing_id': self.sequencing_id,
                'platform_unit': self.platform_unit,
                'platform': self.platform,
                'output_bam': self.temp_output_path,
            }

            self.run_program('picard AddOrReplaceReadGroups', program_options)

        self.rename_extra_temp_output_file('.bai')

    def output(self):
        fn = 'raw_alignment_with_read_groups.bam'
        return luigi.LocalTarget(self.sample_path(fn))

