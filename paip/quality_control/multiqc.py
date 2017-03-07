from paip.task_types import CohortTask
from paip.variant_calling import (
    TrimAdapters,
    AnnotateWithSnpeff,
    AnnotateWithVEP,
)
from paip.quality_control import (
    FastQC,
    #  AlignmentMetrics,
    VariantCallingMetrics,
    VariantEval,
    BcftoolsStats,
    SamtoolsStats,
    FeatureCounts,
)


class MultiQC(CohortTask):
    """
    Expects several quality control programs to have run. Summarizes all those
    results in a single HTML report for the cohort.
    """
    OUTPUT = 'multiqc_report.html'

    def requires(self):
        cohort_tasks = [AnnotateWithVEP]
        cohort_tasks = [task(**self.param_kwargs) for task in cohort_tasks]

        sample_tasks = [
            FastQC,
            TrimAdapters,
            #  AlignmentMetrics,  # SamtoolsStats replaces this
            VariantCallingMetrics,
            AnnotateWithSnpeff,
            VariantEval,
            BcftoolsStats,
            SamtoolsStats,
            FeatureCounts,
        ]

        sample_tasks = [task(sample=sample, **self.param_kwargs)
                        for sample in self.sample_list
                        for task in sample_tasks]

        return cohort_tasks + sample_tasks

    def run(self):
        program_name = 'multiqc'
        program_options = {
            'basedir': self.basedir,
            'report_filename': self.output().fn,
        }
        self.run_program(program_name, program_options)

