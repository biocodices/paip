import pytest

from paip.pipelines.quality_control import DepthOfCoverage


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(DepthOfCoverage)


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk DepthOfCoverage'
    assert program_options['input_bam'] == task.input().fn
    assert 'depth_of_coverage-luigi-tmp' in program_options['outfile']
    assert mock_rename.call_count == 1

