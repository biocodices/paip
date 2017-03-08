import pytest

from paip.pipelines.variant_calling import ResetFilters


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(ResetFilters)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'bcftools reset_filters'
    assert result['program_options']['input_vcf'] == task.input()[0].fn
    assert result['program_options']['output_vcf'] == task.output().fn

