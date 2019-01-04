import os
from os import remove
# NOTE: I need to remove files after testing in these tests, so i'm importing
# remove directly, since os.remove is mocked in conftest.py and set to autouse.
# If you change this here and do something like:
#
#   import os
#
# and then:
#
#   os.remove(fn)
#
# You wil used the mocked version (which is useful in other tests of this
# package, that's why it's set this way.)

from os.path import isfile
from unittest.mock import Mock, patch, PropertyMock

import pytest

import paip
from paip.pipelines.cnv_calling import VisualizeCNVs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(VisualizeCNVs)


def test_run(task, monkeypatch):
    mock_makedirs = Mock(name='makedirs')
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)
    monkeypatch.setattr(paip.pipelines.cnv_calling.VisualizeCNVs,
                        'copy_and_edit_R_script', Mock())

    task.run()

    mock_makedirs.assert_called_once()
    assert mock_makedirs.call_args[0][0].endswith('xhmm_run/plots')

    task.run_command.assert_called_once()

    (command, ), kwargs = task.run_command.call_args

    assert 'Rscript' in command
    assert command.endswith('make_XHMM_plots.R')


def test_copy_and_edit_R_script(task, monkeypatch):
    mock_resources = patch('paip.helpers.config.Config.resources',
                           new_callable=PropertyMock)
    with mock_resources as mock_resources:
        mock_resources.return_value = {
            'panel_annotated_intervals': '/path/to/panel_annotated_intervals',
            'xhmm_R_script': pytest.helpers.file('example_make_XHMM_plots.R'),
        }
        task.copy_and_edit_R_script()

    # Check that a new file with edited variables has been generated
    edited_R_script = pytest.helpers.file('Cohort1/xhmm_run/make_XHMM_plots.R')
    assert isfile(edited_R_script)

    with open(edited_R_script) as f:
        script_lines = [line.strip() for line in f]

    for script_line in script_lines:
        if script_line.startswith('PLOT_PATH = '):
            assert script_line.endswith('Cohort1/xhmm_run/plots"')

        if script_line.startswith('JOB_PREFICES = '):
            assert script_line.endswith('Cohort1/xhmm_run/Cohort1.DATA"')

        if script_line.startswith('JOB_TARGETS_TO_GENES = '):
            assert script_line.endswith('/path/to/panel_annotated_intervals"')

        if script_line.startswith('OTHER_VARIABLE = '):
            assert script_line.endswith('original-value"')

    # Clean afterwards
    remove(edited_R_script)
    assert not isfile(edited_R_script)

