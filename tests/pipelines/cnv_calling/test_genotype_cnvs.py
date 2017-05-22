import pytest

from paip.pipelines.cnv_calling import GenotypeCNVs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(GenotypeCNVs)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'xhmm genotype'
    assert program_options['zscores_matrix'].endswith('sample_zscores.RD.txt')
    assert program_options['read_depth_matrix'].endswith('same_filtered.RD.txt')
    assert program_options['cnvs_file'].endswith('.xcnv')
    assert program_options['output_vcf'].endswith('.vcf')

