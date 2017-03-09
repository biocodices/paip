import pytest

from paip.pipelines.variant_calling import RealignAroundIndels


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(RealignAroundIndels)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk IndelRealigner'
    assert program_options['input_bam'] == task.input()[0].fn
    assert program_options['targets_file'] == task.input()[1].fn
    assert 'realignment.bam-luigi-tmp' in program_options['output_bam']
    assert task.rename_temp_bai.call_count == 1

