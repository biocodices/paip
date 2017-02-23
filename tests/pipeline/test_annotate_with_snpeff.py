import pytest

from paip.pipeline import AnnotateWithSnpeff


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithSnpeff)


def test_run(task, test_cohort_path):
    with pytest.raises(TypeError):
        # This will fail because mock_run_program
        # doesn't return (stdout, stderr). I'd rather
        # have it fail there than later in the open function,
        # which I can't patch, see:
        # http://doc.pytest.org/en/latest/monkeypatch.html
        task.run()
        # It's ok anyway, I can test the rest of the run():

    result = task.run_program.args_received

    assert result['program_name'] == 'snpeff annotate'

    seen_input = result['program_options']['input_vcf']
    assert seen_input == task.input().fn


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('.eff.vcf')

