import pytest

from paip.pipelines.quality_control import FastQC


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(FastQC)


def test_run(task):
    task.run()
    assert task.run_program.call_count == 2

    (program_name, program_options), _ = task.run_program.call_args_list[0]

    assert program_name == 'fastqc'
    assert program_options['forward_reads'] == \
        task.input()['raw_reads']['forward_reads'].path
    assert program_options['reverse_reads'] == \
        task.input()['raw_reads']['reverse_reads'].path

    (program_name, program_options), _ = task.run_program.call_args_list[1]

    assert program_name == 'fastqc'
    assert program_options['forward_reads'] == \
        task.input()['trimmed_reads']['forward_reads'].path
    assert program_options['reverse_reads'] == \
        task.input()['trimmed_reads']['reverse_reads'].path
