import luigi

from paip.task_types import CohortTask


def create_cohort_task(sample_task_class):
    """
    This method is a nice hack to create a CohortTask given a SampleTask.
    We define the new CohortTask as a luigi.WrapperTask that will instantiate
    sample tasks for each of its samples. This behavior is dependent on
    CohortTask.requires() checking for the SAMPLE_REQUIRES class variable.
    """
    name = sample_task_class.__name__ + 'Cohort'
    cohort_task_class = type(name, (CohortTask, luigi.WrapperTask),
                             {'SAMPLE_REQUIRES': sample_task_class})
    return cohort_task_class

