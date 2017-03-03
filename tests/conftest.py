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
def sample_taks_params(test_cohort_basedir):
    return {'basedir': test_cohort_basedir,
            'sample': 'Sample1'}


@pytest.fixture
def cohort_task_params(test_cohort_basedir):
    return {'basedir': test_cohort_basedir,
            'samples': 'Sample1,Sample2',
            'pipeline_type': 'variant_sites'}


@pytest.fixture(scope='function')
def mocks():
    def mock_run_program(program_name, program_options, **kwargs):
        args_received = {
            'program_name': program_name,
            'program_options': program_options,
            **kwargs,
        }

        f = mock_run_program  # Alias for this method
        if hasattr(f, 'args_received'):
            # Store args in a list this was called more than once
            f.args_received = [f.args_received, args_received]
        else:
            f.args_received = args_received

    def mock_os_rename(src, dest):
        if not hasattr(mock_os_rename, 'args_received'):
            mock_os_rename.args_received = []

        mock_os_rename.args_received.append({'src': src, 'dest': dest})

    def mock_rename_idx():
        mock_rename_idx.was_called = True

    def mock_rename_bai():
        mock_rename_bai.was_called = True

    return {
        'run_program': mock_run_program,
        'rename_idx': mock_rename_idx,
        'rename_bai': mock_rename_bai,
        'os_rename': mock_os_rename,
    }


@pytest.fixture(scope='function')
def task_factory(mocks, monkeypatch):
    """
    Returns a function that takes a task class and instantiates it
    with test parameters and mock run_program, rename_temp_bai,
    rename_temp_idx, and os.rename.
    """
    def factory(klass, params, extra_params={}):
        task = klass(**params, **extra_params)

        monkeypatch.setattr(task, 'run_program', mocks['run_program'])
        monkeypatch.setattr(task, 'rename_temp_idx', mocks['rename_idx'])
        monkeypatch.setattr(task, 'rename_temp_bai', mocks['rename_bai'])
        monkeypatch.setattr(os, 'rename', mocks['os_rename'])

        return task

    return factory


@pytest.fixture(scope='function')
def sample_task_factory(task_factory, sample_taks_params):

    def factory(klass, extra_params={}):
        task = task_factory(klass, sample_taks_params, extra_params)
        return task

    return factory


@pytest.fixture(scope='function')
def cohort_task_factory(task_factory, cohort_task_params):

    def factory(klass, extra_params={}):
        task = task_factory(klass, cohort_task_params, extra_params)
        return task

    return factory

