import pytest

from paip.pipelines.cnv_calling import XhmmZscores


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(XhmmZscores)


def test_run(task):
    task.run()

    (program_name, program_options), _ = task.run_program.call_args
    assert program_name == 'xhmm Z_scores'
    assert 'DATA.PCA_normalized.txt' in program_options['pca_normalized_matrix']
    assert ('DATA.PCA_normalized.filtered.sample_zscores.RD.txt' in
            program_options['out_zscores'])
    assert 'filtered_targets.txt' in program_options['out_excluded_targets']
    assert 'filtered_samples.txt' in program_options['out_excluded_samples']

