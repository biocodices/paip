import pytest

from paip.quality_control import VariantCallingMetrics


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(VariantCallingMetrics)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'picard CollectVariantCallingMetrics'
    assert result['program_options']['input_gvcf'] == task.input()[0].fn
    assert result['program_options']['output_txt'] == task.sample

