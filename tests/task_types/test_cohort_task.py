from os.path import expanduser

import pytest

from paip.task_types import CohortTask
from paip.task_types.cohort_task import EmptyCohortException


@pytest.fixture
def cohort_task_all(test_cohort_basedir):
    return CohortTask(basedir=test_cohort_basedir, samples='ALL')


@pytest.fixture
def cohort_task_2(test_cohort_basedir):
    return CohortTask(basedir=test_cohort_basedir, samples='Sample1,Sample2')


def test_find_samples_ALL(test_cohort_basedir):
    found_samples = CohortTask._find_samples(samples='ALL',
                                             basedir=test_cohort_basedir)
    assert found_samples == ['Sample1', 'Sample2', 'Sample3']


def test_find_samples_some(test_cohort_basedir):
    found_samples = CohortTask._find_samples(samples='Sample1,Sample2',
                                             basedir=test_cohort_basedir)
    assert found_samples == ['Sample1', 'Sample2']


def test_find_samples_fail(test_cohort_basedir):
    with pytest.raises(ValueError):
        CohortTask._find_samples(samples='Sample1,SampleNonExistent',
                                 basedir=test_cohort_basedir)


def test_init(cohort_task_all, test_cohort_basedir):
    assert CohortTask(basedir='~', samples='ALL').dir == expanduser('~')
    assert CohortTask(basedir='~/..', samples='ALL').dir == '/home'
    assert cohort_task_all.sample_list == ['Sample1', 'Sample2', 'Sample3']

    # Test default value for pipe type
    assert cohort_task_all.pipeline_type == 'target_sites'

    # Test init kwargs are stored
    assert cohort_task_all.param_kwargs == {
        'basedir': test_cohort_basedir,
        'samples': 'ALL',
        'pipeline_type': 'target_sites',
    }

    # Test it breaks on bad pipeline_type
    with pytest.raises(ValueError):
        CohortTask(basedir=test_cohort_basedir, samples='ALL',
                   pipeline_type='unknown')

    with pytest.raises(EmptyCohortException):
        CohortTask(basedir=pytest.helpers.test_file('Cohort1/Sample1'),
                   samples='ALL')


def test_define_cohort_name(cohort_task_all, cohort_task_2):
    assert cohort_task_all._define_cohort_name() == 'Cohort1__3_Samples'
    assert cohort_task_2._define_cohort_name() == 'Cohort1__2_Samples'


def test_log_path(cohort_task_all):
    assert cohort_task_all.log_path('foo') == 'Cohort1__3_Samples.log.foo'


def test_cohort_path(cohort_task_all):
    assert cohort_task_all.cohort_path('foo').endswith('Cohort1__3_Samples.foo')

