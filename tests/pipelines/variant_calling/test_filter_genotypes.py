import pytest

from paip.pipelines.variant_calling import FilterGenotypes, CombineVariants


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterGenotypes)


def test_requires(task):
    expected_dependencies = CombineVariants(**task.param_kwargs)
    assert task.requires() == expected_dependencies


def test_run(task, test_cohort_path, mock_rename):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T VariantFiltration' in command
    assert task.input().path in command
    assert f'GQ < {task.min_gq}' in command
    assert f'DP < {task.min_dp}' in command
    assert 'geno_filt.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2


def test_output(task, test_cohort_path):
    assert task.output().path.endswith('geno_filt.vcf')

