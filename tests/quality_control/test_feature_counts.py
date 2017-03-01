import pytest

from paip.quality_control import FeatureCounts


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(FeatureCounts)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'featureCounts'
    assert result['program_options']['input_bam'] == task.input().fn
    assert result['program_options']['outfile'] == task.output().fn

