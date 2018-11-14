from paip.pipelines.variant_calling import RealignAroundIndels
from paip.task_types import SampleTask
from paip.helpers.create_cohort_task import create_cohort_task


class FeatureCounts(SampleTask):
    """
    Takes a BAM and creates a summary file of its annotated features from
    a human features GTF file.
    """
    REQUIRES = RealignAroundIndels
    OUTPUT = 'feature_counts'

    def run(self):
        program_name = 'featureCounts'
        program_options = {
            'input_bam': self.input().path,
            'outfile': self.output().path,
        }
        self.run_program(program_name, program_options)

FeatureCountsCohort = create_cohort_task(FeatureCounts)

