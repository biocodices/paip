from os.path import isabs

import pytest

from paip.task_types import SampleTask
from paip.task_types.sample_task import SampleNotFoundError, MissingDataInYML


@pytest.fixture
def sample_task(sample_task_factory):
    return sample_task_factory(SampleTask, sample_name="Sample1")


def test_path(sample_task):
    path = sample_task.path('foo.txt')
    assert isabs(path)
    assert path.endswith('Sample1/Sample1.foo.txt')


def test_paths(sample_task):
    paths = sample_task.paths(['foo.txt', 'bar.txt'])
    expected_paths = ['Sample1/Sample1.foo.txt', 'Sample1/Sample1.bar.txt']
    for path, expected_path in zip(paths, expected_paths):
        assert path.endswith(expected_path)


def test_log_path(sample_task):
    log_path = sample_task.log_path('foo')
    assert log_path.endswith('Sample1/Sample1.log.foo')


def test_load_sample_data_from_yaml(sample_task):
    assert sample_task.flowcell_id == 'Flowcell-ID'
    assert sample_task.library_id == 'Library-ID'
    assert sample_task.platform == 'Platform'
    assert sample_task.lane_numbers_merged == 'Lane1-Lane2'


def test_init(sample_task_factory):
    sample_with_exome = sample_task_factory(sample_name='SampleWithExome')
    sample_with_fastqs = sample_task_factory(sample_name='Sample1')

    assert sample_with_exome.external_exome is True
    assert sample_with_exome.external_sample_name == "External-Name"
    assert sample_with_fastqs.external_exome is False

    with pytest.raises(SampleNotFoundError):
        sample_task_factory(sample_name='SampleNotInYAML')
    with pytest.raises(MissingDataInYML):
        sample_task_factory(sample_name='SampleWithIncompleteInfo')


def test_output(sample_task, test_sample_path):
    # As single element
    sample_task.OUTPUT = 'foo.bar'
    expected_output = test_sample_path('Sample1.foo.bar')
    assert sample_task.output().path == expected_output

    # As list
    sample_task.OUTPUT = ['foo.bar', 'foo.baz']
    expected_outputs = [test_sample_path('Sample1.foo.bar'),
                        test_sample_path('Sample1.foo.baz')]
    assert [out.path for out in sample_task.output()] == expected_outputs


def test_cohort_params(sample_task):
    params = sample_task.cohort_params()
    assert 'sample' not in params
    assert 'basedir' in params

