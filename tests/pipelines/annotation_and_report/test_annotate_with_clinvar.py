import pytest

from paip.pipelines.annotation_and_report import AnnotateWithClinvar


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithClinvar)


#  def test_run(task):
    #  task.run()


def test_output(task):
    assert task.output().fn.endswith('.clinvar_variants.json')
