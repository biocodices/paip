import pytest

from paip.variant_calling import CreateRealignmentIntervals


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(CreateRealignmentIntervals)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk RealignerTargetCreator'
    assert result['program_options']['input_bam'] == task.input().fn
    expected_out = 'realignment.intervals-luigi-tmp'
    assert expected_out in result['program_options']['outfile']

