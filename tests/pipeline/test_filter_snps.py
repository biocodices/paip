import os
import re

import pytest

from paip.pipeline import FilterSNPs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterSNPs)


def test_run(task, test_cohort_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk VariantFiltration snps'

    seen_input = result['program_options']['input_vcf']
    expected_input_fn = 'Cohort1__2_Samples.variant_sites.snps.vcf'
    expected_input = test_cohort_path(expected_input_fn)
    assert seen_input == expected_input

    seen_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'snps.filt.*luigi-tmp.*')
    assert expected_output.search(seen_output)

    assert task.rename_temp_idx.was_called
    assert not task.rename_temp_bai.was_called

    assert os.rename.args_received[0]['src'] == seen_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    fn = 'Cohort1__2_Samples.variant_sites.snps.filt.vcf'
    expected_path = test_cohort_path(fn)
    assert task.output().fn == expected_path

