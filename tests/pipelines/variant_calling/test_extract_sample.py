import pytest

from paip.pipelines.variant_calling import ExtractSample, FilterGenotypes


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(ExtractSample,
                               extra_params={'sample': 'Sample1'})


def test_requires(task, cohort_task_params):
    expected_requires = FilterGenotypes(**cohort_task_params)
    assert task.requires() == expected_requires


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk SelectVariants sample'
    assert program_options['input_vcf'] == task.input().path
    assert 'with_filters.vcf-luigi-tmp' in program_options['output_vcf']
    assert mock_rename.call_count == 2

