import luigi

from paip.task_types import CohortTask
from paip.pipelines.quality_control import DiagnoseTargets
from paip.metrics_generation import CoverageAnalyser
from paip.helpers import path_to_resource


class PlotCoverage(CohortTask):
    """
    Takes the BAM files of a Cohort and generates an HTML report with several
    coverage plots.
    """
    SAMPLE_REQUIRES = DiagnoseTargets

    def output(self):
        fn = f'coverage_report.DP_{self.min_dp}.html'
        return luigi.LocalTarget(self.path(fn))

    def run(self):
        panel_variants = path_to_resource('panel_file_for_coverage_report')

        coverage_analyser = CoverageAnalyser(
            coverage_files=[input_.fn for input_ in self.input()],
            panel=panel_variants,
            reads_threshold=self.min_dp,
        )

        report_title = self.name.replace('_', ' ').title()
        coverage_analyser.report(report_title=report_title,
                                 destination_path=self.output().fn)
