from paip.task_types import CohortTask
from paip.variant_calling import AnnotateWithSnpeffCohort
from paip.quality_control import (
    FastQC,
    AlignmentMetrics,
    VariantCallingMetrics,
)


class MultiQC(CohortTask):
    """
    Expects several quality control programs to have run. Summarizes all those
    results in a single HTML report for the cohort.
    """
    OUTPUT = 'multiqc_report.html'

    def requires(self):
        tasks = [
            FastQC,
            AlignmentMetrics,
            VariantCallingMetrics,
        ]

        sample_tasks = [task(sample=sample, basedir=self.basedir)
                        for sample in self.sample_list
                        for task in tasks]

        return [AnnotateWithSnpeffCohort(**self.param_kwargs)] + sample_tasks

    def run(self):
        program_name = 'multiqc'
        program_options = {
            'basedir': self.basedir,
        }
        self.run_program(program_name, program_options)

