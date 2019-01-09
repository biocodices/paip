from paip.pipelines.annotation import AnnotateDbsnpId


def test_run(cohort_task_factory, test_cohort_path, monkeypatch):
    task = cohort_task_factory(AnnotateDbsnpId,
                               samples='Sample1',
                               cohort_name='IonCohort')

    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'SnpSift.jar annotate -tabix -id -v' in command
    assert task.input().path in command
    assert 'luigi-tmp' in kwargs['redirect_stdout_to_path']
    assert kwargs['log_stdout'] is False

    assert '.dbSNP.vcf' in task.output().path
