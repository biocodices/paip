import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import KeepReportableGenotypes, ExtractSample
from paip.metrics_generation import PanelMetricsGenerator
from paip.helpers.create_cohort_task import create_cohort_task


class PanelMetrics(SampleTask):
    """
    Takes VCF files of unfiltered and reportable variants. For each one,
    it generates metrics of the panel variants (missing %, seen %, etc.),
    JSON-formatted for MultiQC.

    This will only work if the variant calling is done on a panel of variants,
    (that is, a VCF with the panel variants must be available),
    as opposed to a panel of some or all exons.
    """
    REQUIRES = [ExtractSample, KeepReportableGenotypes]

    def run(self):
        settings = [
            ('unfiltered_variants', self.input()[0], self.output()[:2]),
            ('reportable_variants', self.input()[1], self.output()[2:]),
        ]

        for module_name, input_vcf, output_jsons in settings:

            pmg = PanelMetricsGenerator(
                sample_name=self.sample,
                sample_vcf=input_vcf.fn,
                panel_vcf=self.config.resources['panel_variants'],
                min_gq=self.min_gq,
                min_dp=self.min_dp,
            )

            json_metrics = pmg.json_metrics_for_multiqc(
                module_name=module_name
            )

            with open(output_jsons[0].fn, 'w') as f:
                f.write(json_metrics)

            json_data = pmg.json_non_numerical_data()
            with open(output_jsons[1].fn, 'w') as f:
                f.write(json_data)

    def output(self):
        # The _mqc files contain numerical info that will be charted by MultiQC
        # The _data files have non-numerical info.
        outputs = ['unfiltered_variants_mqc.json',
                   'unfiltered_variants_data.json',
                   'reportable_variants_mqc.json',
                   'reportable_variants_data.json']

        return [luigi.LocalTarget(self.path(fn)) for fn in outputs]

PanelMetricsCohort = create_cohort_task(PanelMetrics)

