import pytest

from paip.pipelines.cnv_calling import FilterAndCenterMatrix


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterAndCenterMatrix)


def test_run(task):
    task.run()

    (program_name, program_options), _ = task.run_program.call_args
    assert program_name == 'xhmm centerData'
    assert 'DATA.RD.txt' in program_options['read_depth_matrix']
    assert 'DATA.filtered_centered.RD.txt' in program_options['out_matrix']
    assert 'filtered_targets.txt' in program_options['out_excluded_targets']
    assert 'filtered_samples.txt' in program_options['out_excluded_samples']
    assert 'extreme_gc_targets.txt' in program_options['extreme_gc_targets']

