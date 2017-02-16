import pytest

import paip.task_types


@pytest.fixture
def base_task():
    return paip.task_types.BaseTask()


def test_log_path(base_task):
    assert base_task.log_path('foo') == 'log.foo'


def test_run_program(base_task, monkeypatch):
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

    monkeypatch.setattr(paip.task_types.base_task, 'generate_command',
                        fake_generate_command)
    monkeypatch.setattr(paip.task_types.base_task, 'run_command',
                        fake_run_command)

    args_received = base_task.run_program(
        program_name='program',
        program_options={'foo': 'bar'},
        extra_kwarg='foo'
    )

    # Test the command is the one that comes from generate_command
    assert args_received['command'] == 'program --foo bar'

    # Test the logfile was created from the class name of the Task
    assert args_received['logfile'] == 'log.BaseTask'

    # Test extra kwargs were passed to run_command
    assert args_received['extra_kwarg'] == 'foo'

