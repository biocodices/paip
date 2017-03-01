import pytest

from paip.quality_control import MultiQC


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(MultiQC)


def test_run(task, test_cohort_path):
    task.run()
    result = task.run_program.args_received
    assert result['program_name'] == 'multiqc'
    assert result['program_options']['basedir'] == task.basedir
    assert result['program_options']['report_filename'] == task.output().fn

