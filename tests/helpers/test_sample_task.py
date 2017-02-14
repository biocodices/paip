import paip.helpers

import pytest


@pytest.fixture
def sample_task():
    task = paip.helpers.SampleTask()
    task.sample_id = 'Sample1'
    return task


def test_sample_path(sample_task):
    assert sample_task.sample_path('foo.txt') == 'Sample1/Sample1.foo.txt'


def test_sample_paths(sample_task):
    paths = sample_task.sample_paths(['foo.txt', 'bar.txt'])
    assert paths == ['Sample1/Sample1.foo.txt', 'Sample1/Sample1.bar.txt']


def test_sample_data_from_yaml(sample_task):
    seq_data_yaml = pytest.helpers.test_file('sequencing_data.yml')
    sample_task.load_sample_data_from_yaml(seq_data_yaml)

    assert sample_task.sequencing_id == 'Seq1'
    assert sample_task.library_id == 'Lib1'
    assert sample_task.id_in_sequencing == 'Spl1'
    assert sample_task.platform == 'Plat'
    assert sample_task.platform_unit == 'PlatUnit'


def test_run_program(sample_task, monkeypatch):
    # run_program uses generate_command, but we test that method elsewhere
    # so we just mock it here:
    def fake_generate_command(program_name, options):
        opts = list(options.items())[0]
        return '{} --{} {}'.format(program_name, opts[0], opts[1])

    # run_program also uses run_command to run the command, but we're not
    # interested in testing the actual shell running of the command,
    # (which is tested elsewhere) so we mock that too:
    def fake_run_command(command, logfile, **kwargs):
        arguments_received = {
            'command': command,
            'logfile': logfile,
        }
        arguments_received.update(**kwargs)
        return arguments_received

    monkeypatch.setattr(paip.helpers.sample_task, 'generate_command',
                        fake_generate_command)
    monkeypatch.setattr(paip.helpers.sample_task, 'run_command',
                        fake_run_command)

    args_received = sample_task.run_program(
        program_name='program',
        program_options={'foo': 'bar'},
        extra_kwarg='foo'
    )

    # Test the command is the one that comes from generate_command
    assert args_received['command'] == 'program --foo bar'

    # Test the logfile was created from the class name of the Task
    assert args_received['logfile'] == 'Sample1/Sample1.log.SampleTask'

    # Test extra kwargs were passed to run_command
    assert args_received['extra_kwarg'] == 'foo'

