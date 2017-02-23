import os

import pytest

from paip.pipeline import SplitMultisampleVCF


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(SplitMultisampleVCF)


def test_run(task, test_cohort_path):
    assert 0
    #  task.run()
    #  result = task.run_program.args_received

    # In a for loop for sample_list
    #  assert result['program_name'] == 'vep annotate'

    #  program_input = result['program_options']['input_vcf']
    #  assert program_input == task.input().fn

    #  program_output = result['program_options']['output_vcf']
    #  expected_output = 'vep.vcf-luigi-tmp'
    #  assert expected_output in program_output

    #  assert os.rename.args_received[0]['src'] == program_output
    #  assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('.vep.vcf')


