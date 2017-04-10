import pytest

from paip.pipelines.cnv_calling import FilterPrenormalizedMatrix


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterPrenormalizedMatrix)


def test_run(task):
    task.run()

    (program_name, program_options), _ = task.run_program.call_args
    assert program_name == 'xhmm filter_prenormalized_matrix'
    assert 'DATA.RD.txt' in program_options['read_depth_matrix']
    assert ('DATA.filtered_centered.RD.txt.filtered_targets.txt' in
            program_options['raw_excluded_targets'])
    assert ('DATA.PCA_normalized.filtered.sample_zscores.RD.txt.filtered_targets.txt' in
            program_options['zscore_excluded_targets'])
    assert ('DATA.filtered_centered.RD.txt.filtered_samples.txt' in
            program_options['raw_excluded_samples'])
    assert ('DATA.PCA_normalized.filtered.sample_zscores.RD.txt.filtered_samples.txt' in
            program_options['zscore_excluded_samples'])
    assert 'DATA.same_filtered.RD.txt' in program_options['outfile']

