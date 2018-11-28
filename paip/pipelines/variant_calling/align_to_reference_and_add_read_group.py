from paip.task_types import SampleTask
from paip.pipelines.variant_calling import TrimAdapters
from paip.helpers.create_cohort_task import create_cohort_task


class AlignToReferenceAndAddReadGroup(SampleTask):
    """
    Expects two files: forward and reverse reads of the same sample.
    It will use the reference genome defined in resources.yml to
    map the genes to genomic coordinates.

    It will also add *the same read group* to all reads in the input FASTQ
    files, based on information for the sample found in the seq info YAML.

    Generates a .sam file with the raw alignments.
    """
    REQUIRES = TrimAdapters
    OUTPUT = 'raw_alignment.wrong_rg.sam'

    def run(self):
        program_name = 'bwa'
        program_options = {
            'forward_reads': self.input()['forward_reads'].path,
            'reverse_reads': self.input()['reverse_reads'].path,

            # Info for the read group:
            'library_id': self.library_id,
            'platform': self.platform,
            'platform_unit': self.platform_unit,
            'run_number': self.run_number,
            'flowcell_id': self.flowcell_id,
            'lane_numbers_merged': self.lane_numbers_merged,
            'sample_id': self.sample,
        }

        with self.output().temporary_path() as temp_sam:
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_sam)


AlignToReferenceAndAddReadGroupCohort = \
    create_cohort_task(AlignToReferenceAndAddReadGroup)
