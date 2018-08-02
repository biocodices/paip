import os
from os.path import join, dirname
from unittest.mock import MagicMock, Mock

pytest_plugins = ['helpers_namespace']

import pytest

from paip.helpers import Config, generate_command



@pytest.helpers.register
def file(filename):
    """Return the path to a file/dir under this repo's tests/files."""
    return join(dirname(__file__), 'files', filename)


@pytest.fixture(autouse=True)
def config_example_files(monkeypatch):
    # Read the Config files from paip/example_config:
    app_root_directory = dirname(dirname(__file__))
    monkeypatch.setattr(Config, 'CONFIG_DIR',
                        join(app_root_directory, 'paip/example_config'))


@pytest.fixture
def config_test_files(monkeypatch):
    # Read the Config files from tests/files/config_dir:
    monkeypatch.setattr(Config, 'CONFIG_DIR',
                        pytest.helpers.file('config_dir'))


@pytest.fixture
def test_cohort_basedir():
    return pytest.helpers.file('Cohort1')


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
def task_factory(monkeypatch):
    """
    Returns a function that takes a task class and instantiates it
    with test parameters and mock run_program, rename_temp_bai,
    rename_temp_idx.

    The mocked run_program will check if executables, resources, and commands
    are defined in the example config files, so we keep them updated.
    """

    # This takes the same arguments as BaseTask.run_program
    # and performs some extra checks:
    def extra_checks(program_name, program_options, **kwargs):
        # Test the command is generated correctly with the options passed
        # using the example_config YAML files as models.
        config = Config()
        generate_command(program_name, program_options, config)

        return_value = []

        if not kwargs.get('log_stdout'):
            return_value.append('stdout')

        if not kwargs.get('log_stderr'):
            return_value.append('stderr')

        return return_value


    run_program = MagicMock(side_effect=extra_checks, name='run_program')

    def factory(klass, params, extra_params={}):
        task = klass(**params, **extra_params)

        monkeypatch.setattr(task, 'run_program', run_program)

        return task

    return factory


@pytest.fixture(scope='function', autouse=True)
def mock_rename(monkeypatch):
    mock_rename = MagicMock(name='os.rename')
    monkeypatch.setattr(os, 'rename', mock_rename)
    return mock_rename


@pytest.fixture(scope='function')
def mock_makedirs(monkeypatch):
    mock_makedirs = Mock(name='os.makedirs')
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)
    return mock_makedirs


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

