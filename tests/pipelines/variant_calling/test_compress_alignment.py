import pytest

from paip.pipelines.variant_calling import CompressAlignment


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(CompressAlignment)


def test_run(task, mock_rename, mock_remove):
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'samtools SAM to BAM'
    assert program_options['input_sam'] == task.input().path
    assert mock_rename.call_count == 1 # Renames .bam luigi tempfile
    assert mock_remove.call_count == 1 # Removes the original SAM
    assert mock_remove.call_args[0][0] == task.input().path
    assert task.output().path + '-luigi-tmp' in kwargs['redirect_stdout_to_path']
