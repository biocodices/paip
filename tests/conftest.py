import os
from os.path import join, dirname

pytest_plugins = ['helpers_namespace']

import pytest

from paip.helpers import Config


@pytest.helpers.register
def test_file(filename):
    """Return the path to a file/dir under this repo's tests/files."""
    return join(dirname(__file__), 'files', filename)


@pytest.fixture(autouse=True)
def config_test_files(monkeypatch):
    # Read the Config files from tests/files/config_dir:
    monkeypatch.setattr(Config, 'BASE_DIR',
                        pytest.helpers.test_file('config_dir'))


@pytest.fixture
def test_cohort_basedir():
    return pytest.helpers.test_file('Cohort1')


@pytest.fixture
def test_cohort_path(test_cohort_basedir):
    def func(path):
        return join(test_cohort_basedir, path)
    return func


@pytest.fixture
def test_sample_path(test_cohort_basedir):
    def func(path):
        return join(test_cohort_basedir, 'Sample1', path)
    return func


@pytest.fixture
def test_sample_task_params(test_cohort_basedir):
    return {'basedir': test_cohort_basedir,
            'sample': 'Sample1'}


@pytest.fixture
def test_cohort_task_params(test_cohort_basedir):
    return {'basedir': test_cohort_basedir,
            'samples': 'Sample1,Sample2',
            'pipeline_type': 'variant_sites'}


@pytest.fixture(scope='function')
def cohort_task_factory(test_cohort_task_params, monkeypatch):
    """
    Returns a function that takes a task class and instantiates it
    with test parameters and mock run_program, rename_temp_bai,
    rename_temp_idx, and os.rename.
    """
    def factory(klass):
        task = klass(**test_cohort_task_params)

        def mock_run_program(program_name, program_options, **kwargs):
            mock_run_program.args_received = {
                'program_name': program_name,
                'program_options': program_options,
                **kwargs,
            }

        def mock_os_rename(src, dest):
            if not hasattr(mock_os_rename, 'args_received'):
                mock_os_rename.args_received = []

            mock_os_rename.args_received.append({'src': src, 'dest': dest})

        def mock_rename_idx():
            mock_rename_idx.was_called = True

        mock_rename_idx.was_called = False

        def mock_rename_bai():
            mock_rename_bai.was_called = True

        mock_rename_bai.was_called = False

        monkeypatch.setattr(task, 'run_program', mock_run_program)
        monkeypatch.setattr(task, 'rename_temp_idx', mock_rename_idx)
        monkeypatch.setattr(task, 'rename_temp_bai', mock_rename_bai)
        monkeypatch.setattr(os, 'rename', mock_os_rename)

        return task

    return factory

