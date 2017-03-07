import luigi
import yaml

from paip.task_types import SampleTask
from paip.variant_calling import KeepReportableGenotypes
from paip.metrics_generation import PanelMetricsGenerator
from paip.helpers import path_to_resource
from paip.helpers.create_cohort_task import create_cohort_task


class PanelMetrics(SampleTask):
    REQUIRES = KeepReportableGenotypes

    def run(self):
        pmg = PanelMetricsGenerator(
            sample_vcf=self.input().fn,
            sample_name=self.sample,
            panel_vcf=path_to_resource('panel_variants'),
        )

        pmg.compute_metrics()

        # MultiQC needs this structure:
        metrics = {
            'id': 'panel_metrics',
            'data': pmg.metrics,
        }

        with open(self.output().fn, 'w') as f:
            f.write(yaml.dump(metrics))

    def output(self):
        fp = self.sample_pipeline_path('panel_metrics_mqc.yml')
        return luigi.LocalTarget(fp)

PanelMetricsCohort = create_cohort_task(PanelMetrics)

