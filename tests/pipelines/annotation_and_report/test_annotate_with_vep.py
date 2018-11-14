import pytest

from paip.pipelines.annotation_and_report import AnnotateWithVEP


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithVEP)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'vep annotate'
    assert program_options['input_vcf'] == task.input().path
    assert program_options['output_stats_html'].endswith('_summary.html')
    assert 'luigi-tmp' in program_options['output_vcf']


def test_output(task):
    assert task.output().path.endswith('.vep.tsv')
