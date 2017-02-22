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

