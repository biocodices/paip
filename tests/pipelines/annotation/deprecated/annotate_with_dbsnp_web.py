import pytest

from paip.pipelines.annotation import AnnotateWithDbsnpWeb


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithDbsnpWeb)


def test_output(task):
    assert task.output().path.endswith('.dbsnp_annotations.json')

