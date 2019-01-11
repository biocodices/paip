import re

from paip.pipelines.annotation import AnnotateWithCosmic


def test_run(cohort_task_factory):
    task = cohort_task_factory(AnnotateWithCosmic)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'SnpSift.jar annotate -id -noInfo -v' in command
    assert re.search(r'Cohort1..+.COS.vcf', kwargs['redirect_stdout_to_path'])
