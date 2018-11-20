import pytest

from paip.pipelines.variant_calling import CreateRealignmentIntervals


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(CreateRealignmentIntervals)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 RealignerTargetCreator'
    assert program_options['input_bam'] == task.input().path
    assert 'realignment.intervals-luigi-tmp' in program_options['outfile']

