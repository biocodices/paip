import luigi

from paip.task_types import CohortTask
from paip.pipelines.annotation_and_report import (
    AnnotateWithVEP,
    AnnotateWithSnpeff,
)


class VariantCalling(CohortTask, luigi.WrapperTask):
    """
    Wrapper task to run the complete variant calling pipeline.
    """
    def requires(self):
        cohort_tasks = [
            AnnotateWithVEP(**self.param_kwargs),
        ]
        sample_tasks = [
            AnnotateWithSnpeff(sample=sample, **self.param_kwargs)
            for sample in self.sample_list
        ]
        return cohort_tasks + sample_tasks
