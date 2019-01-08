from paip.pipelines.annotation_and_report import AnnotateGnomadFrequencies


def test_run(cohort_task_factory, test_cohort_path, monkeypatch):
    task = cohort_task_factory(AnnotateGnomadFrequencies,
                               samples='Sample1',
                               cohort_name='IonCohort')

    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'SnpSift.jar annotate -tabix -noId -v' in command
    assert task.input().path in command
    assert 'luigi-tmp' in kwargs['redirect_stdout_to_path']
    assert kwargs['log_stdout'] is False

    assert '.AD.vcf' in task.output().path
