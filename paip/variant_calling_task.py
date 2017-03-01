import luigi

from paip.task_types import CohortTask
from paip.variant_calling import AnnotateWithVEP, AnnotateWithSnpeff
from paip.quality_control import MultiQC


class VariantCalling(CohortTask, luigi.WrapperTask):
    """
    Wrapper task to run the complete variant calling pipeline and then the
    quality control pipeline.
    """
    def requires(self):
        cohort_tasks = [
            AnnotateWithVEP,
            MultiQC,
        ]
        cohort_tasks = [task(**self.param_kwargs) for task in cohort_tasks]

        sample_tasks = [AnnotateWithSnpeff]
        sample_tasks = [task(sample=sample, **self.param_kwargs)
                        for task in sample_tasks
                        for sample in self.sample_list]

        return cohort_tasks + sample_tasks

