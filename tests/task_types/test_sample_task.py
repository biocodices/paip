from os.path import isabs

import paip.task_types

import pytest


@pytest.fixture
def sample_task(test_cohort_basedir):
    task = paip.task_types.SampleTask(basedir=test_cohort_basedir,
                                      sample='Sample1')
    return task


def test_sample_path(sample_task):
    path = sample_task.sample_path('foo.txt')
    assert isabs(path)
    assert path.endswith('Sample1/Sample1.foo.txt')


def test_sample_paths(sample_task):
    paths = sample_task.sample_paths(['foo.txt', 'bar.txt'])
    expected_paths = ['Sample1/Sample1.foo.txt', 'Sample1/Sample1.bar.txt']
    for path, expected_path in zip(paths, expected_paths):
        assert path.endswith(expected_path)


def test_log_path(sample_task):
    log_path = sample_task.log_path('foo')
    assert log_path.endswith('Sample1/Sample1.log.foo')


def test_load_sample_data_from_yaml(sample_task):
    seq_data_yaml = 'sequencing_data.yml'
    sample_task.load_sample_data_from_yaml(seq_data_yaml)

    assert sample_task.sequencing_id == 'Seq1'
    assert sample_task.library_id == 'Lib1'
    assert sample_task.id_in_sequencing == 'Spl1'
    assert sample_task.platform == 'Plat'
    assert sample_task.platform_unit == 'PlatUnit'

