import pytest

from paip.task_types import CohortTask
from paip.task_types.cohort_task import EmptyCohortException


@pytest.fixture
def cohort_task_all(test_cohort_basedir):
    return CohortTask(basedir=test_cohort_basedir,
                      samples='ALL',
                      pipeline_type='variant_sites')


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
    assert cohort_task_all.sample_list == ['Sample1', 'Sample2', 'Sample3']

    # Test default value for pipe type
    assert cohort_task_all.pipeline_type == 'variant_sites'

    # Test init kwargs are stored
    assert cohort_task_all.param_kwargs == {
        'basedir': test_cohort_basedir,
        'samples': 'ALL',
        'pipeline_type': 'variant_sites',
    }

    # Test it breaks on bad pipeline_type
    with pytest.raises(ValueError):
        CohortTask(basedir=test_cohort_basedir, samples='ALL',
                   pipeline_type='unknown')

    with pytest.raises(EmptyCohortException):
        CohortTask(basedir=pytest.helpers.test_file('EmptyCohort'))

    # Won't find a sequencing_data.yml here:
    with pytest.raises(IOError):
        CohortTask(basedir=pytest.helpers.test_file('Cohort1/Sample1'))


def test_define_cohort_name(cohort_task_all, cohort_task_2):
    assert cohort_task_all._define_cohort_name() == 'Cohort1__3_Samples'
    assert cohort_task_2._define_cohort_name() == 'Cohort1__2_Samples'


def test_log_path(cohort_task_all):
    expected_fn = 'Cohort1__3_Samples.variant_sites.log.foo'
    assert cohort_task_all.log_path('foo').endswith(expected_fn)


def test_cohort_path(cohort_task_all):
    expected_fn = 'Cohort1__3_Samples.variant_sites.foo'
    assert cohort_task_all.cohort_path('foo').endswith(expected_fn)

