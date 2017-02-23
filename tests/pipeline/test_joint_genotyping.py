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

    seen_inputs = result['program_options']['input_gvcfs']
    expected_inputs = ['Sample1.g.vcf', 'Sample2.g.vcf']
    expected_inputs = [
        '-V ' + test_sample_path(expected_inputs[0]),
        # FIXME: Ugly hack, this should be done better:
        '-V ' + test_sample_path(expected_inputs[0]).replace('Sample1', 'Sample2'),
    ]
    assert seen_inputs == ' '.join(expected_inputs)

    seen_output = result['program_options']['output_vcf']
    expected_output = re.compile(r'vcf-luigi-tmp')
    assert expected_output.search(seen_output)

    assert task.rename_temp_idx.was_called
    assert not task.rename_temp_bai.was_called

    assert os.rename.args_received[0]['src'] == seen_output
    assert os.rename.args_received[0]['dest'] == task.output().fn


def test_output(task, test_cohort_path):
    expected = test_cohort_path('Cohort1__2_Samples.variant_sites.vcf')
    assert task.output().fn == expected

