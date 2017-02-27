import os
import re

import pytest

from paip.variant_calling import FilterIndels


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterIndels)


def test_run(task, test_cohort_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk VariantFiltration indels'

    program_input = result['program_options']['input_vcf']
    expected_input_fn = 'Cohort1__2_Samples.variant_sites.indels.vcf'
    expected_input = test_cohort_path(expected_input_fn)
    assert program_input == expected_input

    program_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'indels.filt.*luigi-tmp.*')
    assert expected_output.search(program_output)

    assert task.rename_temp_idx.was_called

    assert os.rename.args_received[0]['src'] == program_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('indels.filt.vcf')

