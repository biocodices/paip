import pytest

from paip.pipelines.variant_calling import AddOrReplaceReadGroups


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(AddOrReplaceReadGroups)


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'picard AddOrReplaceReadGroups'
    assert program_options['input_bam'] == task.input().path
    assert program_options['library_id'] == 'Library-ID'
    assert program_options['flowcell_id'] == 'Flowcell-ID'
    assert program_options['lane_number'] == 'Lane-Number'
    assert program_options['platform'] == 'Platform'
    assert task.output().path + '-luigi-tmp' in program_options['output_bam']
    assert mock_rename.call_count == 2
