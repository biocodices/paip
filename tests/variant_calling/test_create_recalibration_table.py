import pytest

from paip.variant_calling import CreateRecalibrationTable


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(CreateRecalibrationTable)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk BaseRecalibrator'
    assert result['program_options']['input_bam'] == task.input().fn
    expected_out = 'recalibration_table-luigi-tmp'
    assert expected_out in result['program_options']['outfile']

