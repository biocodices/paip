from paip.task_types import SampleTask
from paip.pipelines.variant_calling import SortCompressPutReadGroups
from paip.helpers.create_cohort_task import create_cohort_task


class MarkDuplicates(SampleTask):
    """
    Takes the sorted BAM from the alignment and removes duplicate reads.
    """
    REQUIRES = SortCompressPutReadGroups
    OUTPUT = {
        'deduped_bam': 'deduped_alignment.sorted.with_rg.bam',
        'metrics_file': 'deduped_alignment.metrics.txt'
    }

    def run(self):
        with self.output()['deduped_bam'].temporary_path() as self.temp_bam, \
             self.output()['metrics_file'].temporary_path() as temp_metrics_file:

            program_name = 'picard MarkDuplicates'
            program_options = {
                'input_bam': self.input().path,
                'output_bam': self.temp_bam,
                'output_metrics_file': temp_metrics_file
            }

            self.run_program(program_name, program_options)


MarkDuplicatesCohort = create_cohort_task(MarkDuplicates)
