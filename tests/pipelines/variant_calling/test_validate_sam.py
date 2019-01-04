import pytest

from unittest.mock import mock_open, patch
from paip.pipelines.variant_calling import ValidateSam
from paip.pipelines.variant_calling.validate_sam import InvalidSamException


def test_run(sample_task_factory):
    task = sample_task_factory(ValidateSam)

    open_ = mock_open(read_data='No errors found')

    # FIXME: this whole 'path' to the module hardcoding is ugly, but I need
    # the regular builtin open() to be operational for the rest of the code:
    with patch('paip.pipelines.variant_calling.validate_sam.open', open_):
        task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'picard-2.18.16.jar ValidateSamFile' in command
    assert task.input().path in command
    assert task.output().path + '-luigi-tmp-' in command

    open_.assert_called_once_with(task.output().path)

    open_ = mock_open(read_data='Some error text')
    with patch('paip.pipelines.variant_calling.validate_sam.open', open_):
        with pytest.raises(InvalidSamException):
            task.run()
