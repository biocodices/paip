import os
from os.path import join

from paip.task_types import CohortTask
from paip.pipelines.quality_control import DiagnoseTargets
from paip.metrics_generation import CoverageAnalyser
from paip.helpers import path_to_resource, SomeTarget


class PlotCoverage(CohortTask):
    """
    Takes the BAM files of a Cohort and generates one plot of coverage
    per chromosome under the dir `coverage_plots`.
    """
    SAMPLE_REQUIRES = DiagnoseTargets

    def run(self):
        coverage_analyser = CoverageAnalyser(
            panel_vcf=path_to_resource('panel_variants'),
            coverage_files=[input_.fn for input_ in self.input()],
            reads_threshold=self.min_dp,
        )

        os.makedirs(self.outdir, exist_ok=True)

        coverage_analyser.plot(out_base_path=join(self.outdir, 'coverage'))

    def output(self):
        self.outdir = self.cohort_path('coverage_plots')
        return SomeTarget(self.outdir, '.png')

