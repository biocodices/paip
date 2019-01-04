from paip.pipelines.quality_control import DiagnoseTargets


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(DiagnoseTargets)
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T DiagnoseTargets' in command
    assert task.input()['dupmarked_bam'].path in command
    assert f'--minimum_coverage {task.min_dp}' in command
    assert 'coverage_diagnosis.vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2
