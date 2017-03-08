from unittest.mock import mock_open, patch
import pytest

from paip.pipelines.variant_calling import AlignToReference


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(AlignToReference)


def test_run(task):
    open_ = mock_open()

    # FIXME: this whole 'path' to the module hardcoding is ugly, there must
    # be a better way:
    with patch('paip.pipelines.variant_calling.align_to_reference.open', open_):
        task.run()

    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'bwa'
    assert program_options['forward_reads'] == task.input()[0].fn
    assert program_options['reverse_reads'] == task.input()[1].fn
    assert kwargs['log_stdout'] is False
    open_().write.assert_called_once_with('stdout')
