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
    OUTPUT = 'coverage_report.html'

    def run(self):
        try:
            panel_variants = path_to_resource('panel_variants')
        except KeyError:  # variant_sites pipelines might not have a panel VCF
            panel_variants = None

        coverage_analyser = CoverageAnalyser(
            coverage_files=[input_.fn for input_ in self.input()],
            panel=panel_variants,
            reads_threshold=self.min_dp,
        )

        report_title = self.name.replace('_', ' ').title()
        coverage_analyser.report(report_title=report_title,
                                 destination_path=self.output().fn)


