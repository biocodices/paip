import pytest
import luigi

from paip.task_types import CohortTask, SampleTask
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
    expected_samples = [
        'Sample1',
        'Sample2',
        'Sample3',
        'SampleWithExome',
        'SampleWithoutExome',
    ]
    assert found_samples == expected_samples


def test_find_samples_some(cohort_task_all):
    found_samples = cohort_task_all._find_samples(samples='Sample1,Sample2')
    assert found_samples == ['Sample1', 'Sample2']


def test_find_samples_fail(cohort_task_all):
    with pytest.raises(ValueError):
        cohort_task_all._find_samples(samples='Sample1,SampleNonExistent')


def test_init(cohort_task_all, test_cohort_basedir):
    # Test the sample list is populated
    assert cohort_task_all.sample_list

    # Test default value for pipe type
    assert cohort_task_all.pipeline_type == 'variant_sites'

    assert cohort_task_all.name == 'Cohort1'

    # Test init kwargs are stored
    assert cohort_task_all.param_kwargs == {
        'basedir': test_cohort_basedir,

        # Also tests defaults:
        'samples': 'ALL',
        'pipeline_type': 'variant_sites',
        'min_dp': 30,
        'min_gq': 30,
        'trim_software': 'cutadapt',
        'num_threads': 1,
    }

    # Test it breaks on bad pipeline_type
    with pytest.raises(ValueError):
        CohortTask(basedir=test_cohort_basedir, samples='ALL',
                   pipeline_type='unknown')

    with pytest.raises(EmptyCohortException):
        CohortTask(basedir=pytest.helpers.file('EmptyCohort'))

    # Won't find a sequencing_data.yml here:
    with pytest.raises(IOError):
        CohortTask(basedir=pytest.helpers.file('Cohort1/Sample1'))


def test_log_path(cohort_task_all):
    expected_fn = 'Cohort1.log.foo'
    assert cohort_task_all.log_path('foo').endswith(expected_fn)


def test_sample_path(cohort_task_all):
    result = cohort_task_all.sample_path('foo', 'Sample1')
    assert result.endswith('Sample1/Sample1.foo')


def test_sample_requires(cohort_task_params):
    class MockSampleTask(SampleTask):
        pass

    class MockCohortTask(CohortTask, luigi.WrapperTask):
        SAMPLE_REQUIRES = MockSampleTask

    cohort_task = MockCohortTask(**cohort_task_params)
    assert list(cohort_task.sample_requires()) == [
        MockSampleTask(sample='Sample1', **cohort_task_params),
        MockSampleTask(sample='Sample2', **cohort_task_params),
    ]

    # Check that sample requires is correctly assigned as requires()
    # when SAMPLE_REQUIRES variable is present:
    assert list(cohort_task.sample_requires()) == list(cohort_task.requires())


def test_ion_cohort():
    task = CohortTask(basedir=pytest.helpers.file('IonCohort'),
                      samples='ALL',
                      pipeline_type='variant_sites',
                      min_dp=30,
                      min_gq=30)
    assert task.ion is True
