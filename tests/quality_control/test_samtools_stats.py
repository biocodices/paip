import pytest

from paip.quality_control import SamtoolsStats


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(SamtoolsStats)


def test_run(task):
    with pytest.raises(TypeError):
        # FIXME: This test is a hack, the failure is because we try to extract
        # stdout, stderr from run_command but its mock version returns None
        task.run()

    result = task.run_program.args_received
    assert result['program_name'] == 'samtools stats'
    assert result['program_options']['input_bam'] == task.input().fn

