import os
import re

import pytest

from paip.variant_calling import CombineVariants


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(CombineVariants)


def test_run(task, test_cohort_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk CombineVariants snps_indels'

    program_input_snps = result['program_options']['input_snps']
    assert program_input_snps == task.input()[0].fn

    program_input_indels = result['program_options']['input_indels']
    assert program_input_indels == task.input()[1].fn

    program_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'filt.*luigi-tmp.*')
    assert expected_output.search(program_output)

    assert task.rename_temp_idx.was_called

    assert os.rename.args_received[0]['src'] == program_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('filt.vcf')

