import os
from os.path import join, dirname
from unittest.mock import MagicMock, Mock

pytest_plugins = ['helpers_namespace']

import pytest

import paip
from paip.helpers import Config
from paip.task_types import SampleTask, CohortTask



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


@pytest.fixture(scope='function')
def task_factory(monkeypatch):
    """
    Returns a function that takes a task class and instantiates it
    with test parameters and mock run_program, rename_temp_bai,
    rename_temp_idx.

    The mocked run_program will check if executables, resources, and commands
    are defined in the example config files, making sure we keep those
    example configs updated.
    """
    mock_run_command = Mock(return_value=(b'stdout', b'stderr')) ##
    monkeypatch.setattr(paip.helpers, 'run_command', mock_run_command) ##

    def factory(klass, params, extra_params={}):
        task = klass(**params, **extra_params)
        task.run_command = mock_run_command

        old_run_program = task.run_program
        def run_program_with_print(*args, **kwargs):
            result = old_run_program(*args, **kwargs)
            print(f"Running:\n {result[0]}\n") # command
            return result
        task.run_program = run_program_with_print

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


@pytest.fixture(scope='function', autouse=True)
def mock_remove(monkeypatch):
    mock_remove = MagicMock(name='os.remove')
    monkeypatch.setattr(os, 'remove', mock_remove)
    return mock_remove


@pytest.fixture(scope='function')
def sample_task_factory(task_factory):

    def factory(klass=SampleTask,
                extra_params={},
                cohort_name='Cohort1',
                sample_name='Sample1'):

        cohort_dir = pytest.helpers.file(cohort_name)
        sample_task_params = {'basedir': cohort_dir, 'sample': sample_name}
        task = task_factory(klass, sample_task_params, extra_params)

        return task

    return factory


@pytest.fixture
def cohort_task_params(test_cohort_basedir):
    return {'basedir': test_cohort_basedir,
            'samples': 'Sample1,Sample2',
            'pipeline_type': 'variant_sites'}


@pytest.fixture(scope='function')
def cohort_task_factory(task_factory):

    def factory(klass=CohortTask,
                extra_params={},
                cohort_name='Cohort1',
                samples='ALL',
                pipeline_type='variant_sites'):

        cohort_dir = pytest.helpers.file(cohort_name)
        cohort_params = {'basedir': cohort_dir,
                         'samples': samples,
                         'pipeline_type': pipeline_type}
        task = task_factory(klass, cohort_params, extra_params)
        return task

    return factory
