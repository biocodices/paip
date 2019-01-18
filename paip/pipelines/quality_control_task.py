import luigi

from paip.task_types import CohortTask
from paip.pipelines.quality_control import (
    MultiQC,
    PlotCoverage,
    SamtoolsDepthCohort
)


class QualityControl(CohortTask, luigi.WrapperTask):
    """
    Wrapper task to run the complete quality control pipeline.
    """
    def requires(self):
        return [
            # These must be CohortTasks
            MultiQC(**self.param_kwargs),
            PlotCoverage(**self.param_kwargs),
            SamtoolsDepthCohort(**self.param_kwargs)
        ]
