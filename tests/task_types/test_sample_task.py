from os.path import isabs

import pytest

import paip.task_types


@pytest.fixture
def sample_task(test_cohort_basedir):
    task = paip.task_types.SampleTask(basedir=test_cohort_basedir,
                                      sample='Sample1')
    return task


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
    assert sample_task.lane_number == 'Lane-Number'


def test_output(sample_task, test_sample_path):
    # As single element
    sample_task.OUTPUT = 'foo.bar'
    expected_output = test_sample_path('Sample1.foo.bar')
    assert sample_task.output().fn == expected_output

    # As list
    sample_task.OUTPUT = ['foo.bar', 'foo.baz']
    expected_outputs = [test_sample_path('Sample1.foo.bar'),
                        test_sample_path('Sample1.foo.baz')]
    assert [out.fn for out in sample_task.output()] == expected_outputs

