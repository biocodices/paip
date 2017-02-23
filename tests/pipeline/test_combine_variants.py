import os
import re

import pytest

from paip.pipeline import CombineVariants


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(CombineVariants)


def test_run(task, test_cohort_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk CombineVariants snps_indels'

    seen_input_snps = result['program_options']['input_snps']
    assert seen_input_snps == task.input()[0].fn

    seen_input_indels = result['program_options']['input_indels']
    assert seen_input_indels == task.input()[1].fn

    seen_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'filt.*luigi-tmp.*')
    assert expected_output.search(seen_output)

    assert task.rename_temp_idx.was_called
    assert not task.rename_temp_bai.was_called

    assert os.rename.args_received[0]['src'] == seen_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('filt.vcf')

