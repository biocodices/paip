from paip.task_types import SampleTask
from paip.pipelines.quality_control import DiagnoseTargets
from paip.metrics_generation import CoverageAnalyser
from paip.helpers.create_cohort_task import create_cohort_task


class SummarizeCoverage(SampleTask):
    """
    Takes a VCF as produced by GATK's DiagnoseTargets and generates
    a JSON summary of the coverage metrics for MultiQC.
    """
    REQUIRES = DiagnoseTargets
    OUTPUT = {
        'for_multiqc': 'coverage_summary_mqc.json',
        'for_reports': 'coverage_summary.csv',
        'for_reports_per_gene': 'coverage_summary_per_gene.csv',
        'plot_for_reports': 'coverage_distribution.png',
    }

    def run(self):
        try:
            panel = self.config.resources['panel_variants']
        except KeyError:  # variant_sites pipelines might not have a panel VCF
            panel = self.config.resources['panel_file_for_coverage_report']
        except KeyError:
            panel = None

        coverage_analyser = CoverageAnalyser(
            panel=panel,
            coverage_files=[self.input().fn],
            reads_threshold=self.min_dp,
        )

        json_data = coverage_analyser.json_coverage_summary_for_multiqc(
            sample_id=self.sample,
            module_name='coverage_summary',
        )

        with open(self.output()['for_multiqc'].fn, 'w') as f:
            f.write(json_data)

        coverage_analyser.coverage_summary(
            target_csv_path=self.output()['for_reports'].fn
        )
        coverage_analyser.coverage_summary_per_gene(
            target_csv_path=self.output()['for_reports_per_gene'].fn
        )
        coverage_analyser.plot_coverage_distribution(dest_dir=self.dir)


SummarizeCoverageCohort = create_cohort_task(SummarizeCoverage)
