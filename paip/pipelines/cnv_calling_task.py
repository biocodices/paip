import luigi

from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import VisualizeCNVs


class CNVCalling(CohortTask, luigi.WrapperTask):
    """
    Wrapper task to run the complete CNV Calling pipeline.
    """
    REQUIRES = VisualizeCNVs

