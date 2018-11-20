import pytest

from paip.pipelines.variant_calling import RealignAroundIndels


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(RealignAroundIndels)


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 IndelRealigner'
    assert program_options['input_bam'] == task.input()[0].path
    assert program_options['targets_file'] == task.input()[1].path
    assert 'realignment.bam-luigi-tmp' in program_options['output_bam']
    assert mock_rename.call_count == 2

