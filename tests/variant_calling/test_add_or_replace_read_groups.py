import pytest

from paip.variant_calling import AddOrReplaceReadGroups


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(AddOrReplaceReadGroups)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'picard AddOrReplaceReadGroups'

    program_input = result['program_options']['input_sam']
    assert program_input == task.input().fn

    program_input = result['program_options']['sample_barcode']
    assert program_input == 'Sample-Barcode'

    program_input = result['program_options']['library_id']
    assert program_input == 'Library-ID'

    program_output = result['program_options']['flowcell_id']
    assert program_output == 'Flowcell-ID'

    program_output = result['program_options']['lane_number']
    assert program_output == 'Lane-Number'

    program_output = result['program_options']['platform']
    assert program_output == 'Platform'

    program_output = result['program_options']['output_bam']
    assert task.output().fn + '-luigi-tmp' in program_output

    assert task.rename_temp_bai.was_called

