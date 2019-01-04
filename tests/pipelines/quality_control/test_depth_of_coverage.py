from paip.pipelines.quality_control import DepthOfCoverage


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(DepthOfCoverage)
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T DepthOfCoverage' in command
    assert task.input()['dupmarked_bam'].path in command
    assert 'depth_of_coverage-luigi-tmp' in command

    assert mock_rename.call_count == 7  # 1 output file + 6 extra
