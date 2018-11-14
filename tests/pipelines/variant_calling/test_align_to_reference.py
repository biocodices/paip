import pytest

from paip.pipelines.variant_calling import AlignToReference


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(AlignToReference)


def test_run(task):
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'bwa'
    assert program_options['forward_reads'] == task.input()[0].path
    assert program_options['reverse_reads'] == task.input()[1].path
    assert task.output().path + '-luigi-tmp' in kwargs['redirect_stdout_to_path']
