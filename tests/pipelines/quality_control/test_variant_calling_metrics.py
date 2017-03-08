import pytest

from paip.pipelines.quality_control import VariantCallingMetrics


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(VariantCallingMetrics)


def test_run(task):
    task.run()

    assert task.run_program.call_count == 1
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'picard CollectVariantCallingMetrics'
    assert program_options['input_vcf'] == task.input().fn
    assert program_options['output_txt'].endswith('QC')

