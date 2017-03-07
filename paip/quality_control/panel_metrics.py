import luigi

from paip.task_types import SampleTask
from paip.variant_calling import KeepReportableGenotypes, ExtractSample
from paip.metrics_generation import PanelMetricsGenerator
from paip.helpers import path_to_resource
from paip.helpers.create_cohort_task import create_cohort_task


class PanelMetrics(SampleTask):
    """
    Takes VCF files of unfiltered and reportable variants. For each one,
    it generates metrics of the panel variants (missing %, seen %, etc.),
    JSON-formatted for MultiQC.
    """
    REQUIRES = [ExtractSample, KeepReportableGenotypes]

    def run(self):
        settings = {
            ('unfiltered_variants', self.input()[0], self.output()[0]),
            ('reportable_variants', self.input()[1], self.output()[1]),
        }

        for module_name, input_vcf, output_json in settings:

            pmg = PanelMetricsGenerator(
                sample_name=self.sample,
                sample_vcf=input_vcf.fn,
                panel_vcf=path_to_resource('panel_variants'),
                min_gq=self.min_gq,
                min_dp=self.min_dp,
            )

            json_metrics = pmg.json_metrics_for_multiqc(
                module_name=module_name
            )

            with open(output_json.fn, 'w') as f:
                f.write(json_metrics)

    def output(self):
        outputs = ['unfiltered_variants_mqc.json',
                   'reportable_variants_mqc.json']

        return [luigi.LocalTarget(self.sample_pipeline_path(fn))
                for fn in outputs]

PanelMetricsCohort = create_cohort_task(PanelMetrics)

