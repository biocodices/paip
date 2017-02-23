import os
import re

import pytest

from paip.pipeline import MergeVCFs, CallTargets


@pytest.fixture
def task(test_cohort_task_params):
    test_cohort_task_params['pipeline_type'] = 'target_sites'
    return MergeVCFs(**test_cohort_task_params)


def test_requires(task):
    expected_dependencies = [
        CallTargets(sample='Sample1', basedir=task.basedir),
        CallTargets(sample='Sample2', basedir=task.basedir)
    ]
    assert task.requires() == expected_dependencies


@pytest.mark.skip(reason='Fix this test')
def test_run(task, test_sample_path):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk CombineVariants'

    seen_inputs = result['program_options']['input_vcfs']
    expected_inputs = ['Sample1.vcf', 'Sample2.vcf']
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

