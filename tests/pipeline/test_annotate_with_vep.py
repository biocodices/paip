import os

import pytest

from paip.pipeline import AnnotateWithVEP


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithVEP)


def test_run(task, test_cohort_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'vep annotate'

    program_input = result['program_options']['input_vcf']
    assert program_input == task.input().fn

    program_output = result['program_options']['output_vcf']
    assert 'luigi-tmp' in program_output

    assert os.rename.args_received[0]['src'] == program_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('.vep.tsv')

