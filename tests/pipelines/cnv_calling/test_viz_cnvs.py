import os
from os.path import isfile
from unittest.mock import MagicMock

import pytest

import paip
from paip.pipelines.cnv_calling import VizCNVs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(VizCNVs)


def test_run(task, monkeypatch):
    mock_makedirs = MagicMock(name='makedirs')
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)

    task.run()

    mock_makedirs.assert_called_once()
    assert mock_makedirs.call_args[0][0].endswith('xhmm_run/plots')

    task.run_program.assert_called_once()
    (program_name, program_options), _ = task.run_program.call_args
    assert program_name == 'Rscript make_XHMM_plots'
    assert program_options['script_path'].endswith('make_XHMM_plots.R')


def test_copy_and_edit_R_script(task, monkeypatch):

    def test_resources(label):
        if label == 'panel_annotated_intervals':
            return '/path/to/panel_annotated_intervals'
        elif label == 'xhmm_R_script':
            return pytest.helpers.file('example_make_XHMM_plots.R')
        else:
            raise ValueError('Resource "{}" not mocked in this test'
                             .format(label))

    monkeypatch.setattr(paip.pipelines.cnv_calling.viz_cnvs,
                        'path_to_resource', test_resources)

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
    os.remove(edited_R_script)
    assert not isfile(edited_R_script)

