import os
import re

import pytest

from paip.pipeline import FilterGenotypes, CombineVariants


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterGenotypes)


def test_requires(task):
    expected_dependencies = CombineVariants(**task.param_kwargs)
    assert task.requires() == expected_dependencies


def test_run(task, test_cohort_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk VariantFiltration genos'

    program_input = result['program_options']['input_vcf']
    assert program_input == task.input().fn

    program_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'geno_filt.*luigi-tmp.*')
    assert expected_output.search(program_output)

    assert task.rename_temp_idx.was_called

    assert os.rename.args_received[0]['src'] == program_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('geno_filt.vcf')

