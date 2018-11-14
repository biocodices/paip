import pytest

from paip.pipelines.quality_control import SamtoolsDepth


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(SamtoolsDepth)


def test_run(task):
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args
    assert program_name == 'samtools depth'
    assert program_options['input_bam'] == task.input().path
    assert task.output().path in kwargs['redirect_stdout_to_path']
