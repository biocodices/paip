import pytest

from paip.variant_calling import AlignToReference


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(AlignToReference)


def test_run(task):
    with pytest.raises(TypeError):
        # This will fail because mock_run_program
        # doesn't return (stdout, stderr). I'd rather
        # have it fail there than later in the open function,
        # which I can't patch, see:
        # http://doc.pytest.org/en/latest/monkeypatch.html
        task.run()
        # It's ok anyway, I can test the rest of the run():

    result = task.run_program.args_received

    assert result['program_name'] == 'bwa'

    program_input = result['program_options']['forward_reads']
    assert program_input == task.input()[0].fn

    program_input = result['program_options']['reverse_reads']
    assert program_input == task.input()[1].fn

    assert result['log_stdout'] is False

