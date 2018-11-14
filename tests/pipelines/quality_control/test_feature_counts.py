import pytest

from paip.pipelines.quality_control import FeatureCounts


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(FeatureCounts)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'featureCounts'
    assert program_options['input_bam'] == task.input().path
    assert program_options['outfile'] == task.output().path

