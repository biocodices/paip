import luigi

from paip.task_types import CohortTask
from paip.pipelines.quality_control import MultiQC, PlotCoverage


class QualityControl(CohortTask, luigi.WrapperTask):
    """
    Wrapper task to run the complete quality control pipeline.
    """
    def requires(self):
        cohort_tasks = [MultiQC(**self.param_kwargs),
                        PlotCoverage(**self.param_kwargs)]
        return cohort_tasks

