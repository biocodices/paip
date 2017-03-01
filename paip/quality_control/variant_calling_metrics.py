from paip.task_types import SampleTask
from paip.variant_calling import MakeGVCF


class VariantCallingMetrics(SampleTask):
    """
    Expects a gVCF file. Runs Picard tools to generate variant calling  metrics.
    """
    REQUIRES = MakeGVCF
    OUTPUT = ['QC.variant_calling_detail_metrics',
              'QC.variant_calling_summary_metrics']

    def run(self):
        program_name = 'picard CollectVariantCallingMetrics'
        program_options = {
            'input_gvcf': self.input()[0].fn,
            'output_txt': self.sample_path('QC'),
            # ^ The file extension of both output files will be added by Picard
        }
        self.run_program(program_name, program_options)

