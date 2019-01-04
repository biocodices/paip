from paip.pipelines.variant_calling import KeepReportableGenotypes


def test_run(cohort_task_factory, mock_rename):
    task = cohort_task_factory(KeepReportableGenotypes,
                               extra_params={'sample': 'Sample1',
                                             'min_dp': 30,
                                             'min_gq': 30})

    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T SelectVariants' in command

    assert task.input().path in command
    assert 'reportable.vcf-luigi-tmp' in command
    assert f'>= {task.min_dp}' in command
    assert task.sample in command

    assert mock_rename.call_count == 2
