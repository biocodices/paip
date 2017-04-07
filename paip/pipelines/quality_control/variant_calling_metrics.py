from paip.task_types import SampleTask
from paip.pipelines.variant_calling import KeepReportableGenotypes


class VariantCallingMetrics(SampleTask):
    """
    Expects a VCF file. Runs Picard tools to generate variant calling metrics.
    """
    REQUIRES = KeepReportableGenotypes
    OUTPUT = ['QC.variant_calling_detail_metrics',
              'QC.variant_calling_summary_metrics']

    def run(self):
        program_name = 'picard CollectVariantCallingMetrics'
        program_options = {
            'input_vcf': self.input().fn,
            'output_txt': self.path('QC'),
            # ^ The file extension of both output files will be added by Picard
        }
        self.run_program(program_name, program_options)

