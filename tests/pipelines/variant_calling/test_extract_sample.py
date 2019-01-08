from paip.pipelines.variant_calling import ExtractSample, FilterGenotypes


def test_requires(sample_task_factory):
    task = sample_task_factory(
        ExtractSample,
        sample_name='Sample1',
        cohort_name='Cohort1',
    )
    assert isinstance(task.requires(), FilterGenotypes)


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(
        ExtractSample,
        sample_name='Sample1',
        cohort_name='Cohort1',
    )
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T SelectVariants'
    assert task.input().path in command
    assert 'with_filters.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2

