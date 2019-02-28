import re

from paip.pipelines.annotation import AnnotateWithSnpeff


def test_run(cohort_task_factory):
    task = cohort_task_factory(AnnotateWithSnpeff)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'snpEff.jar ann GRCh37.p13.RefSeq' in command
    assert 'Cohort1.snpEff.summary.csv' in command
    assert re.search(r'Cohort1..+.eff.vcf', kwargs['redirect_stdout_to_path'])
