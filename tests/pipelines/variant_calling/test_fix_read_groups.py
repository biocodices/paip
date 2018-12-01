from unittest.mock import Mock, patch

from paip.pipelines.variant_calling import FixReadGroups
import paip


def test_run(sample_task_factory, monkeypatch):
    task = sample_task_factory(FixReadGroups)
    mock_fix_sam_read_groups = Mock()

    with patch('paip.pipelines.variant_calling.fix_read_groups.fix_sam_read_groups',
               mock_fix_sam_read_groups):
        task.run()

    assert mock_fix_sam_read_groups.call_count == 1
    sam_input = mock_fix_sam_read_groups.call_args[1]['sam_input']
    out_path = mock_fix_sam_read_groups.call_args[1]['out_path']
    assert sam_input == task.input().path
    assert task.output().path + '-luigi-tmp-' in out_path
