import pytest

from paip.pipelines.annotation_and_report import AnnotateWithDbsnpWeb


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithDbsnpWeb)


def test_output(task):
    assert task.output().fn.endswith('.dbsnp_annotations.json')


def test_run(task):
    task.run()
    assert 0  # Implement this!
