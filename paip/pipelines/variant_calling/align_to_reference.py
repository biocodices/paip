from paip.task_types import SampleTask
from paip.pipelines.variant_calling import TrimAdapters
from paip.helpers.create_cohort_task import create_cohort_task


class AlignToReference(SampleTask):
    """
    Expects two files: forward and reverse reads of the same sample.
    It will use the reference genome defined in resources.yml to
    map the genes to genomic coordinates.

    Generates a .sam file with the raw alignments.
    """
    REQUIRES = TrimAdapters
    OUTPUT = 'raw_alignment.sam'

    def run(self):
        program_name = 'bwa'
        program_options = {
            'forward_reads': self.input()['forward_reads'].path,
            'reverse_reads': self.input()['reverse_reads'].path,
        }

        with self.output().temporary_path() as temp_sam:
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_sam)


AlignToReferenceCohort = create_cohort_task(AlignToReference)
