from paip.helpers import available_resources
from paip.task_types import CohortTask
from paip.pipelines.variant_calling import TrimAdapters
from paip.pipelines.annotation_and_report import AnnotateWithSnpeff
from paip.pipelines.quality_control import (
    FastQC,
    BcftoolsStats,
    SamtoolsStats,
    PanelMetrics,
    SummarizeCoverage,
)


class MultiQC(CohortTask):
    """
    Expects several quality control programs to have run. Summarizes all those
    results in a single HTML report for the cohort.
    """
    OUTPUT = 'multiqc_report.html'

    def requires(self):
        sample_tasks = [
            FastQC,
            TrimAdapters,
            AnnotateWithSnpeff,
            BcftoolsStats,
            SamtoolsStats,
            SummarizeCoverage,
        ]

        # Some pipelines might not have a VCF of panel variants
        # (e.g. exomes, exon panels like Trusight Cardio)
        if 'panel_variants' in available_resources():
            sample_tasks.append(PanelMetrics)

        sample_tasks = [task(sample=sample, **self.param_kwargs)
                        for sample in self.sample_list
                        for task in sample_tasks]

        return sample_tasks

    def run(self):
        program_name = 'multiqc'
        program_options = {
            'basedir': self.basedir,
            'report_filename': self.output().fn,
        }
        self.run_program(program_name, program_options)

