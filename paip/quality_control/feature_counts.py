from paip.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask


class FeatureCounts(SampleTask):
    """
    Takes a BAM and creates a summary file of its annotated features from
    a human features GTF file.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'feature_counts'

    def run(self):
        program_name = 'featureCounts'
        program_options = {
            'input_bam': self.input().fn,
            'outfile': self.output().fn,
        }
        self.run_program(program_name, program_options)

