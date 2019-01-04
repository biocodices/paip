import pytest

from paip.pipelines.cnv_calling import GenotypeCNVs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(GenotypeCNVs)


def test_run(task):
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --genotype' in command
    assert 'Cohort1.DATA.PCA_normalized.filtered.sample_zscores.RD.txt' in command
    assert 'Cohort1.DATA.same_filtered.RD.txt' in command
    assert 'Cohort1.DATA.xcnv' in command
    assert 'Cohort1.DATA.vcf' in command

