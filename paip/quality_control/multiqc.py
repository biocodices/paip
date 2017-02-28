from paip.task_types import CohortTask
from paip.variant_calling import AnnotateWithSnpeffCohort
from paip.quality_control import (
    FastQC,
    AlignmentMetrics,
    VariantCallingMetrics,
    VariantEval,
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

        cohort_tasks = [
            AnnotateWithSnpeffCohort,
            VariantEval,
        ]
        cohort_tasks = [task(**self.param_kwargs) for task in cohort_tasks]

        return cohort_tasks + sample_tasks

    def run(self):
        program_name = 'multiqc'
        program_options = {
            'basedir': self.basedir,
        }
        self.run_program(program_name, program_options)

