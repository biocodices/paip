import os

import pytest

from paip.pipelines.variant_calling import KeepReportableGenotypes, ExtractSample


@pytest.fixture
def task(cohort_task_factory):
    extra_params = {'sample': 'Sample1', 'min_dp': 30, 'min_gq': 30}
    return cohort_task_factory(KeepReportableGenotypes,
                               extra_params=extra_params)


def test_requires(task, cohort_task_params):
    expected_requires = ExtractSample(**cohort_task_params,
                                      sample=task.sample)
    assert task.requires() == expected_requires


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk SelectVariants reportable'

    program_input = result['program_options']['input_vcf']
    assert program_input == task.input().fn

    program_output = result['program_options']['output_vcf']
    expected_output = 'reportable.vcf-luigi-tmp'
    assert expected_output in program_output

    assert result['program_options']['min_GQ'] == 30
    assert result['program_options']['min_DP'] == 30
    assert result['program_options']['sample'] == task.sample

    assert task.rename_temp_idx.was_called

    assert os.rename.args_received[0]['src'] == program_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task):
    assert task.output().fn.endswith('variant_sites.reportable.vcf')

