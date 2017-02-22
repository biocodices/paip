import pytest
import luigi

import paip.task_types


@pytest.fixture
def base_task():
    return paip.task_types.BaseTask()


@pytest.fixture
def MockTask():

    class MockClass(paip.task_types.BaseTask):
        param = luigi.Parameter()

    return MockClass


def fake_rename(src, dest):
    # Fake function used to test the parameters that the
    # actual rename function will receive.
    if not hasattr(fake_rename, 'received_parameters'):
        fake_rename.received_parameters = []

    fake_rename.received_parameters.append({'src': src, 'dest': dest})


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


def test_find_output(base_task):
    output_files = ['foo.bar', 'bar.baz', 'qux.baz']
    output_files = [luigi.LocalTarget(fn) for fn in output_files]
    base_task.output = lambda: output_files

    assert base_task._find_output('baz').fn == 'bar.baz'

    # Works with only one file in the output:
    base_task.output = lambda: output_files[0]
    assert base_task._find_output('bar').fn == 'foo.bar'

    with pytest.raises(ValueError):
        base_task._find_output('nonexistent')


def test_rename_temp_bai(base_task, monkeypatch):
    monkeypatch.setattr(paip.task_types.base_task, 'rename', fake_rename)

    base_task.output = lambda: luigi.LocalTarget('out.bam')
    base_task.temp_bam = 'temp.bam'
    base_task.rename_temp_bai()

    expected_parameters = {'src': 'temp.bam.bai', 'dest': 'out.bam.bai'}
    assert expected_parameters in fake_rename.received_parameters


def test_rename_temp_idx(base_task, monkeypatch):
    monkeypatch.setattr(paip.task_types.base_task, 'rename', fake_rename)

    base_task.output = lambda: luigi.LocalTarget('out.bam')
    base_task.temp_bam = 'temp.bam'
    base_task.rename_temp_bai()

    expected_parameters = {'src': 'temp.bam.bai', 'dest': 'out.bam.bai'}
    assert expected_parameters in fake_rename.received_parameters


def test_requires(MockTask):
    mock_task = MockTask(param='param-value')

    # As single element
    mock_task.REQUIRES = MockTask
    assert mock_task.requires() == MockTask(**mock_task.param_kwargs)

    # As list
    mock_task.REQUIRES = [MockTask, MockTask]
    assert mock_task.requires() == [MockTask(**mock_task.param_kwargs),
                                    MockTask(**mock_task.param_kwargs)]


