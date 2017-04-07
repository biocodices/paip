from paip.task_types import SampleTask
from paip.helpers.create_cohort_task import create_cohort_task


def test_create_cohort_task(cohort_task_params):

    class MockSampleTask(SampleTask):
        pass

    CohortTask = create_cohort_task(MockSampleTask)
    cohort_task = CohortTask(**cohort_task_params)

    assert cohort_task.requires() == [
        MockSampleTask(sample='Sample1', **cohort_task_params),
        MockSampleTask(sample='Sample2', **cohort_task_params),
    ]

