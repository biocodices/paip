from paip.pipelines.variant_calling import FilterGenotypes, CombineVariants, MergeVCFs


def test_requires(cohort_task_factory):
    task = cohort_task_factory(
        FilterGenotypes,
        cohort_name='IonCohort',
    )
    expected_dependency = MergeVCFs(**task.param_kwargs)
    assert task.requires() == expected_dependency

    task = cohort_task_factory(
        FilterGenotypes,
        cohort_name='Cohort1',
    )
    expected_dependency = CombineVariants(**task.param_kwargs)
    assert task.requires() == expected_dependency


def test_run(cohort_task_factory, mock_rename):
    task = cohort_task_factory(
        FilterGenotypes,
        cohort_name='Cohort1',
        samples='Sample1',
    )
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T VariantFiltration' in command
    assert 'Cohort1.filt.vcf' in command
    assert f'GQ < {task.min_gq}' in command
    assert f'DP < {task.min_dp}' in command
    assert 'Cohort1.filt.geno_filt.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2


def test_run_from_ion_cohort(cohort_task_factory, mock_rename):
    task = cohort_task_factory(
        FilterGenotypes,
        cohort_name='IonCohort',
        samples='Sample1',
    )
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T VariantFiltration' in command
    assert 'IonCohort.vcf' in command
    assert f'GQ < {task.min_gq}' in command
    assert f'DP < {task.min_dp}' in command
    assert 'IonCohort.geno_filt.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2


def test_output(cohort_task_factory, test_cohort_path):
    task = cohort_task_factory(
        FilterGenotypes,
        cohort_name='IonCohort',
        samples='Sample1',
    )
    assert task.output().path.endswith('geno_filt.vcf')

