import pytest

from paip.pipelines.variant_calling import RecalibrateAlignmentScores


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(RecalibrateAlignmentScores)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk PrintReads'
    assert program_options['input_bam'] == task.input()[0].fn
    assert program_options['recalibration_table'] == task.input()[1].fn
    expected_out = 'recalibrated.bam-luigi-tmp'
    assert expected_out in program_options['output_bam']
    assert task.rename_temp_bai.call_count == 1

