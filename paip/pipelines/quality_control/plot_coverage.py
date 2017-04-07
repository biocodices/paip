from paip.task_types import CohortTask
from paip.pipelines.quality_control import DiagnoseTargets
from paip.metrics_generation import CoverageAnalyser
from paip.helpers import path_to_resource


class PlotCoverage(CohortTask):
    """
    Takes the BAM files of a Cohort and generates one plot of coverage
    per chromosome under the dir `coverage_plots`.
    """
    SAMPLE_REQUIRES = DiagnoseTargets
    OUTPUT = 'coverage_report.html'

    def run(self):
        coverage_analyser = CoverageAnalyser(
            panel_vcf=path_to_resource('panel_variants'),
            coverage_files=[input_.fn for input_ in self.input()],
            reads_threshold=self.min_dp,
        )

        report_title = self.name.replace('_', ' ').title()
        coverage_analyser.report(report_title=report_title,
                                 destination_path=self.output().fn)

