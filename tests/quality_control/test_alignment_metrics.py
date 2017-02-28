import pytest

from paip.quality_control import AlignmentMetrics


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(AlignmentMetrics)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'picard CollectAlignmentSummaryMetrics'

    program_input = result['program_options']['input_bam']
    assert program_input == task.input().fn

    program_output = result['program_options']['output_txt']
    assert 'alignment_metrics.txt-luigi-tmp' in program_output

