import pytest

from paip.pipelines.variant_calling import MergeVCFs, ResetFilters
from paip.pipelines.ion_torrent import TorrentVariantCaller


def test_requires(cohort_task_factory):
    task = cohort_task_factory(
        MergeVCFs,
        cohort_name='Cohort1',
        samples='Sample1,Sample2',
        pipeline_type='target_sites',
    )
    expected_dependencies = [
        ResetFilters(sample='Sample1', basedir=task.basedir),
        ResetFilters(sample='Sample2', basedir=task.basedir),
    ]
    assert task.requires() == expected_dependencies


def test_ion_requires(cohort_task_factory):
    task = cohort_task_factory(
        MergeVCFs,
        cohort_name='IonCohort',
        samples='Sample1',
        pipeline_type='target_sites',
    )
    expected_dependencies = [
        TorrentVariantCaller(sample='Sample1', basedir=task.basedir),
    ]
    assert task.requires() == expected_dependencies


def test_run_from_ion(mock_rename, cohort_task_factory):
    task = cohort_task_factory(
        MergeVCFs,
        cohort_name='IonCohort',
        samples='Sample1',
    )
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert mock_rename.call_count == 2

    assert 'GenomeAnalysisTK.jar -T CombineVariants' in command
    assert 'Sample1.vcf' in command
    assert 'IonCohort.vcf-luigi-tmp' in command

def test_run_from_target_sites(mock_rename, cohort_task_factory):
    task = cohort_task_factory(
        MergeVCFs,
        cohort_name='Cohort1',
        samples='Sample1,Sample2',
    )
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert mock_rename.call_count == 2

    assert 'GenomeAnalysisTK.jar -T CombineVariants' in command
    assert 'Sample1.no_filters.vcf' in command
    assert 'Sample2.no_filters.vcf' in command
    assert 'Cohort1.vcf-luigi-tmp' in command
