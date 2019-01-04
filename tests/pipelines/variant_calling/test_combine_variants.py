import pytest

from paip.pipelines.variant_calling import CombineVariants


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(CombineVariants)


def test_run(task, test_cohort_path, mock_rename):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T CombineVariants' in command
    assert task.input()[0].path in command
    assert task.input()[1].path in command
    assert 'filt.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2


def test_output(task, test_cohort_path):
    assert task.output().path.endswith('filt.vcf')
