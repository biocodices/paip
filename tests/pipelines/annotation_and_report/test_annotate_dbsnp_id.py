from paip.pipelines.ion_torrent import AnnotateDbsnpId


def test_run(sample_task_factory, test_cohort_path, monkeypatch):
    task = sample_task_factory(AnnotateDbsnpId,
                               sample_name='Sample1',
                               cohort_name='IonCohort')

    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'SnpSift.jar annotate -tabix -id -v' in command
    assert task.input()['gzipped_vcf'].path in command
    assert 'luigi-tmp' in kwargs['redirect_stdout_to_path']
    assert kwargs['log_stdout'] is False

    assert task.output().path.endswith('.dbSNP.vcf.gz')
