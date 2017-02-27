import os

import pytest

from paip.quality_control import FastQC


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(FastQC)


def test_run(task):
    task.run()
    result_1, result_2 = task.run_program.args_received

    assert result_1['program_name'] == 'fastqc'
    assert result_1['program_options']['forward_reads'] == task.input()[0][0].fn
    assert result_1['program_options']['reverse_reads'] == task.input()[0][1].fn

    assert result_2['program_name'] == 'fastqc'
    assert result_2['program_options']['forward_reads'] == task.input()[1][0].fn
    assert result_2['program_options']['reverse_reads'] == task.input()[1][1].fn

