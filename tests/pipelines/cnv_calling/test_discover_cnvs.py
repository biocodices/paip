import pytest

from paip.pipelines.cnv_calling import DiscoverCNVs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(DiscoverCNVs)


def test_run(task):
    task.run()

    (program_name, program_options), _ = task.run_program.call_args
    assert program_name == 'xhmm discover'
    assert program_options['data_files_basename'].endswith('DATA')
    assert ('DATA.PCA_normalized.filtered.sample_zscores.RD.txt' in
            program_options['zscores_matrix'])
    assert ('DATA.same_filtered.RD.txt'
            in program_options['read_depth_matrix_filtered'])
    assert 'DATA.xcnv' in program_options['outfile']
    assert 'DATA.aux_xcnv' in program_options['aux_outfile']

