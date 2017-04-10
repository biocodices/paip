import pytest

from paip.pipelines.cnv_calling import XhmmPCANormalization


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(XhmmPCANormalization)


def test_run(task):
    task.run()

    (program_name, program_options), _ = task.run_program.call_args
    assert program_name == 'xhmm PCA_normalization'
    assert 'DATA.filtered_centered.RD.txt' in program_options['filtered_centered_matrix']
    assert 'DATA.RD_PCA' in program_options['pca_files_basename']
    assert 'DATA.PCA_normalized.txt' in program_options['outfile']

