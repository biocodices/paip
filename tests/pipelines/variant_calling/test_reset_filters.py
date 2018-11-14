import pytest

from paip.pipelines.variant_calling import ResetFilters


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(ResetFilters)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'bcftools reset_filters'
    assert program_options['input_vcf'] == task.input()[0].path
    assert program_options['output_vcf'] == task.output().path

