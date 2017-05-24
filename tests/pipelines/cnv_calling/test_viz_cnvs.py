import pytest

from paip.pipelines.cnv_calling import VizCNVs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(VizCNVs)


def test_run(task):
    task.run()

    (program_name, program_options), _ = task.run_program.call_args
