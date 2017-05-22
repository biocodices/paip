import pytest

from paip.pipelines.cnv_calling import MergeGATKDepths


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(MergeGATKDepths)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'xhmm MergeGATKDepths'
    assert 'DATA.RD.txt' in program_options['outfile']

    cvg_files = ['Sample1.depth_of_coverage.sample_coverage_summary',
                 'Sample2.depth_of_coverage.sample_coverage_summary']

    for cvg_file in cvg_files:
        assert cvg_file in program_options['sample_cvg_files']

