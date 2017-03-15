from unittest.mock import mock_open, patch
import pytest

from paip.pipelines.quality_control import SamtoolsDepth


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(SamtoolsDepth)


def test_run(task):
    open_ = mock_open()

    # FIXME: this whole 'path' to the module hardcoding is ugly, there must
    # be a better way:
    with patch('paip.pipelines.quality_control.samtools_depth.open', open_):
        task.run()

    (program_name, program_options), kwargs = task.run_program.call_args
    assert program_name == 'samtools depth'
    assert program_options['input_bam'] == task.input().fn
    assert kwargs['log_stdout'] is False
    open_().write.assert_called_once_with('stdout')

