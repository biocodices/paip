import pytest

from paip.pipelines.quality_control import MultiQC


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(MultiQC)


def test_run(task, test_cohort_path):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'multiqc'
    assert program_options['basedir'] == task.basedir
    assert program_options['report_filename'] == task.output().fn

