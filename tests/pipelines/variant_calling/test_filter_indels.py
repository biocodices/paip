import pytest

from paip.pipelines.variant_calling import FilterIndels


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterIndels)


def test_run(task, mock_rename):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T VariantFiltration' in command
    assert task.input().path in command
    assert 'indels.filt.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2


def test_output(task):
    assert task.output().path.endswith('indels.filt.vcf')

