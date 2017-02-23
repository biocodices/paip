import os
import re

import pytest

from paip.pipeline import JointGenotyping, MakeGVCF


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(JointGenotyping)


def test_requires(task):
    expected_dependencies = [MakeGVCF(sample='Sample1', basedir=task.basedir),
                             MakeGVCF(sample='Sample2', basedir=task.basedir)]
    assert task.requires() == expected_dependencies


def test_run(task, test_cohort_path, test_sample_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk GenotypeGVCFs variant_sites'

    program_inputs = result['program_options']['input_gvcfs']
    expected_inputs = '-V {} -V {}'.format(*[i[0].fn for i in task.input()])
    assert program_inputs == expected_inputs

    program_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'vcf-luigi-tmp')
    assert expected_output.search(program_output)

    assert task.rename_temp_idx.was_called
    assert not task.rename_temp_bai.was_called

    assert os.rename.args_received[0]['src'] == program_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('.vcf')

