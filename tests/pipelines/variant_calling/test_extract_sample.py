import pytest

from paip.pipelines.variant_calling import ExtractSample, FilterGenotypes


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(ExtractSample,
                               extra_params={'sample': 'Sample1'})


def test_requires(task, cohort_task_params):
    expected_requires = FilterGenotypes(**cohort_task_params)
    assert task.requires() == expected_requires


def test_run(task, mock_rename):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T SelectVariants'
    assert task.input().path in command
    assert 'with_filters.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2

