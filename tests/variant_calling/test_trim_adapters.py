import pytest

from paip.variant_calling import TrimAdapters


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(TrimAdapters)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'cutadapt'

    program_input = result['program_options']['forward_reads']
    assert program_input == task.input()[0].fn

    program_input = result['program_options']['reverse_reads']
    assert program_input == task.input()[1].fn

    program_output = result['program_options']['forward_output']
    assert program_output == task.output()[0].fn

    program_output = result['program_options']['reverse_output']
    assert program_output == task.output()[1].fn

