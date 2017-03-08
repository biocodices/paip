import os
from os.path import join, dirname
from unittest.mock import MagicMock

pytest_plugins = ['helpers_namespace']

import pytest

from paip.helpers import Config


@pytest.helpers.register
def file(filename):
    """Return the path to a file/dir under this repo's tests/files."""
    return join(dirname(__file__), 'files', filename)


@pytest.fixture(autouse=True)
def config_test_files(monkeypatch):
    # Read the Config files from tests/files/config_dir:
    monkeypatch.setattr(Config, 'BASE_DIR',
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
    """
    def factory(klass, params, extra_params={}):
        task = klass(**params, **extra_params)

        monkeypatch.setattr(task, 'run_program',
                            MagicMock(return_value=('stdout', 'stderr')))
        monkeypatch.setattr(task, 'rename_temp_idx', MagicMock())
        monkeypatch.setattr(task, 'rename_temp_bai', MagicMock())
        monkeypatch.setattr(os, 'rename', MagicMock())

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

