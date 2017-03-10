import pytest

from paip.pipelines.variant_calling import TrimAdapters


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(TrimAdapters)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'cutadapt'
    assert program_options['forward_reads'] == task.input()[0].fn
    assert program_options['reverse_reads'] == task.input()[1].fn
    assert program_options['forward_output'] == task.output()[0].fn
    assert program_options['reverse_output'] == task.output()[1].fn
