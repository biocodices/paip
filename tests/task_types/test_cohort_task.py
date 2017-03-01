import pytest

from paip.task_types import CohortTask
from paip.task_types.cohort_task import EmptyCohortException


@pytest.fixture
def cohort_task_all(test_cohort_basedir):
    return CohortTask(basedir=test_cohort_basedir,
                      samples='ALL',
                      pipeline_type='variant_sites',
                      min_dp=30,
                      min_gq=30)


@pytest.fixture
def cohort_task_2(test_cohort_basedir):
    return CohortTask(basedir=test_cohort_basedir, samples='Sample1,Sample2')


def test_find_samples_ALL(cohort_task_all):
    found_samples = cohort_task_all._find_samples(samples='ALL')
    assert found_samples == ['Sample1', 'Sample2', 'Sample3']


def test_find_samples_some(cohort_task_all):
    found_samples = cohort_task_all._find_samples(samples='Sample1,Sample2')
    assert found_samples == ['Sample1', 'Sample2']


def test_find_samples_fail(cohort_task_all):
    with pytest.raises(ValueError):
        cohort_task_all._find_samples(samples='Sample1,SampleNonExistent')


def test_init(cohort_task_all, test_cohort_basedir):
    assert cohort_task_all.sample_list == ['Sample1', 'Sample2', 'Sample3']

    # Test default value for pipe type
    assert cohort_task_all.pipeline_type == 'variant_sites'

    # Test init kwargs are stored
    assert cohort_task_all.param_kwargs == {
        'basedir': test_cohort_basedir,
        'samples': 'ALL',
        'pipeline_type': 'variant_sites',
        'min_dp': 30,
        'min_gq': 30
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


def test_sample_path(cohort_task_all):
    result = cohort_task_all.sample_path('foo', 'Sample1')
    assert result.endswith('Sample1/Sample1.{}.foo'
                           .format(cohort_task_all.pipeline_type))

    # Test it uses self.sample if no sample is provided
    cohort_task_all.sample = 'Sample2'
    result = cohort_task_all.sample_path('foo')
    assert result.endswith('Sample2/Sample2.{}.foo'
                           .format(cohort_task_all.pipeline_type))

