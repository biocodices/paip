from paip.task_types import SampleTask
from paip.pipelines.quality_control import DiagnoseTargets
from paip.metrics_generation import CoverageAnalyser
from paip.helpers import path_to_resource


class SummarizeCoverage(SampleTask):
    """
    Takes a VCF as produced by GATK's DiagnoseTargets and generates
    a JSON summary of the coverage metrics for MultiQC.
    """
    REQUIRES = DiagnoseTargets
    OUTPUT = 'coverage_summary_mqc.json'

    def run(self):
        coverage_analyser = CoverageAnalyser(
            panel_vcf=path_to_resource('panel_variants'),
            coverage_files=[self.input().fn],
            reads_threshold=self.min_dp,
        )

        json_data = coverage_analyser.json_coverage_summary_for_multiqc(
            sample_id=self.sample,
            module_name='Coverage Summary',
        )

        with open(self.output().fn, 'w') as f:
            f.write(json_data)

