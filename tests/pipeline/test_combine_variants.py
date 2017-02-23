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

    seen_input_indels = result['program_options']['input_indels']
    expected_input_indels = 'Cohort1__2_Samples.variant_sites.indels.filt.vcf'
    expected_input_indels = test_cohort_path(expected_input_indels)
    assert seen_input_indels == expected_input_indels

    seen_input_snps = result['program_options']['input_snps']
    expected_input_snps = 'Cohort1__2_Samples.variant_sites.snps.filt.vcf'
    expected_input_snps = test_cohort_path(expected_input_snps)
    assert seen_input_snps == expected_input_snps

    seen_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'filt.*luigi-tmp.*')
    assert expected_output.search(seen_output)

    assert task.rename_temp_idx.was_called
    assert not task.rename_temp_bai.was_called

    assert os.rename.args_received[0]['src'] == seen_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    fn = 'Cohort1__2_Samples.variant_sites.filt.vcf'
    expected_path = test_cohort_path(fn)
    assert task.output().fn == expected_path

