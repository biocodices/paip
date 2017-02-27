import pytest

from paip.variant_calling import RealignAroundIndels


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(RealignAroundIndels)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk IndelRealigner'
    assert result['program_options']['input_bam'] == task.input()[0].fn
    assert result['program_options']['targets_file'] == task.input()[1].fn
    expected_out = 'realignment.bam-luigi-tmp'
    assert expected_out in result['program_options']['output_bam']
    assert task.rename_temp_bai.was_called

