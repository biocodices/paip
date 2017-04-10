import pytest

from paip.pipelines.cnv_calling import GCContentByInterval


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(GCContentByInterval)


def test_run(task):
    task.run()

    (program_name, program_options), _ = task.run_program.call_args_list[0]
    assert program_name == 'gatk GCContentByInterval'
    assert 'DATA.locus_GC.txt' in program_options['outfile']

    (program_name, program_options), _ = task.run_program.call_args_list[1]
    assert program_name == 'awk extreme_GC_targets'
    assert 'DATA.locus_GC.txt' in program_options['gc_content_by_interval']
    assert 'extreme_gc_targets.txt' in program_options['outfile']

