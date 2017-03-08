import pytest

from paip.pipelines.variant_calling import AnnotateWithVEP


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithVEP)


def test_run(task, test_cohort_path):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'vep annotate'

    program_input = program_options['input_vcf']
    assert program_input == task.input().fn

    program_output = program_options['output_vcf']
    assert 'luigi-tmp' in program_output


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('.vep.tsv')

