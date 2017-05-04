from paip.helpers import available_resources
from paip.task_types import CohortTask
from paip.pipelines.variant_calling import (
    TrimAdapters,
    AnnotateWithSnpeff,
    AnnotateWithVEP,
)
from paip.pipelines.quality_control import (
    FastQC,
    #  AlignmentMetrics,
    #  VariantCallingMetrics,
    #  VariantEval,
    BcftoolsStats,
    SamtoolsStats,
    FeatureCounts,
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
        cohort_tasks = [AnnotateWithVEP]
        cohort_tasks = [task(**self.param_kwargs) for task in cohort_tasks]

        sample_tasks = [
            FastQC,
            TrimAdapters,
            #  AlignmentMetrics,  # SamtoolsStats replaces this
            #  VariantCallingMetrics,  # MultiQC doesn't use this
            AnnotateWithSnpeff,
            #  VariantEval,  # The count of SNPs seems to be wrong, misleading!
            BcftoolsStats,
            SamtoolsStats,
            FeatureCounts,
        ]

        if 'panel_variants' in available_resources():
            # These tasks need the VCF of target variants:
            sample_tasks += [
                PanelMetrics,
                SummarizeCoverage,
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

