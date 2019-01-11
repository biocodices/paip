import re

from paip.pipelines.annotation import AnnotateWithClinvarVcf


def test_run(cohort_task_factory):
    task = cohort_task_factory(AnnotateWithClinvarVcf)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'SnpSift.jar annotate -tabix -noId -v -name CLINVAR_' in command
    assert re.search(r'Cohort1..+.clin.vcf', kwargs['redirect_stdout_to_path'])
