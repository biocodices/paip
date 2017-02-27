import os

import pytest

from paip.variant_calling import ExtractSample, FilterGenotypes


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(ExtractSample,
                               extra_params={'sample': 'Sample1'})


def test_requires(task, test_cohort_task_params):
    expected_requires = FilterGenotypes(**test_cohort_task_params)
    assert task.requires() == expected_requires


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk SelectVariants sample'

    program_input = result['program_options']['input_vcf']
    assert program_input == task.input().fn

    program_output = result['program_options']['output_vcf']
    expected_output = 'with_filters.vcf-luigi-tmp'
    assert expected_output in program_output

    assert task.rename_temp_idx.was_called

    assert os.rename.args_received[0]['src'] == program_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task):
    assert task.output().fn.endswith('.with_filters.vcf')

