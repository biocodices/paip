from os import remove # The unmocked remove
from pathlib import Path

from paip.pipelines.variant_calling import DeleteSamFiles


def test_run(sample_task_factory, mock_remove):
    task = sample_task_factory(DeleteSamFiles)
    task.run()
    assert mock_remove.call_count == 2 # .fixed_rg.sam and .wrong_rg.sam
    call1, call2 = mock_remove.call_args_list
    inpath_1 = task.input()['wrong_rg_alignment'].path
    inpath_2 = task.input()['fixed_rg_alignment'].path
    assert call1[0][0] == inpath_1
    assert call2[0][0] == inpath_2

    Path(inpath_1).touch()
    Path(inpath_2).touch()
    assert not task.complete()

    remove(inpath_1) # unmocked remove, works 4 real
    remove(inpath_2) # unmocked remove, works 4 real
    assert task.complete()
