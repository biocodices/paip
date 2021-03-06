import time
import os
from unittest.mock import MagicMock

import pytest
import luigi
from luigi.tools.luigi_grep import LuigiGrep

import paip.task_types


@pytest.fixture
def base_task(test_cohort_basedir):
    return paip.task_types.BaseTask(basedir=test_cohort_basedir)


@pytest.fixture
def MockTask():

    class MockClass(paip.task_types.BaseTask):
        param = luigi.Parameter(default='foo')
        OUTPUT = 'some-file.foo'
        dir = 'some-dir'
        name = 'Name'

    return MockClass


def test_init(test_cohort_basedir, monkeypatch):
    # Test it creates a subdirectory if needed
    class SomeCohortTask(paip.task_types.BaseTask):
        SUBDIR = 'foo'

    mock_makedirs = MagicMock()
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)

    task = SomeCohortTask(basedir=test_cohort_basedir)

    assert mock_makedirs.call_count == 1
    assert mock_makedirs.call_args[0][0].endswith('foo')

    assert task.config.custom_config_dir == test_cohort_basedir


def test_path(base_task):
    # self.dir and self.name is defined in the subclasses, so here I pretend
    # this was done like in a CohortTask:
    base_task.dir = base_task.basedir
    base_task.name = 'Cohort1'

    assert base_task.path('foo.txt').endswith('Cohort1/Cohort1.foo.txt')

    base_task.SUBDIR = 'some_subdir'

    expected = 'Cohort1/some_subdir/Cohort1.foo.txt'
    assert base_task.path('foo.txt').endswith(expected)

    expected = 'Cohort1/some_subdir/foo.txt'
    assert base_task.path('foo.txt', prefix=False).endswith(expected)

    # Clean the fixture base_task for other tests:
    del(base_task.dir)
    del(base_task.name)
    del(base_task.SUBDIR)


def test_load_sample_data_from_yaml(base_task):
    # By default, sequencing_data.yml is read
    for key in ['Sample1', 'Sample2', 'Sample3']:
        assert key in base_task.sequencing_data

    # But the method can take a filename as argument
    other_data = base_task.load_sample_data_from_yaml('other_seq_data.yml')
    assert other_data['foo'] == 'bar'

    # If the YAML file is empty, return an empty dict, not None
    base_task.basedir = base_task.basedir.replace('Cohort1', 'EmptyCohort')
    empty_seq_data = base_task.load_sample_data_from_yaml('sequencing_data.yml')
    assert empty_seq_data == {}

    base_task.basedir = base_task.basedir.replace('EmptyCohort', 'IonCohort')
    ion_data = base_task.load_sample_data_from_yaml('sequencing_data.yml')
    assert ion_data['Sample1']['external_sample_name'] == 'Sample-1-External-Name'
    assert ion_data['Sample1']['ion'] is True


def test_output(base_task, monkeypatch, MockTask):
    # These are defined in CohortTask and SampleTask
    base_task.name = 'BaseTask'
    base_task.dir = '/path/to/BaseTask'

    with pytest.raises(Exception):
        base_task.output()

    base_task.OUTPUT = 'foo'
    assert base_task.output().path.endswith('BaseTask/BaseTask.foo')

    base_task.OUTPUT = ['foo', 'bar']
    outputs = base_task.output()
    assert outputs[0].path.endswith('BaseTask/BaseTask.foo')
    assert outputs[1].path.endswith('BaseTask/BaseTask.bar')

    base_task.OUTPUT = {'foo': 'foo', 'bar': 'bar'}
    outputs = base_task.output()
    assert outputs['foo'].path.endswith('BaseTask/BaseTask.foo')
    assert outputs['bar'].path.endswith('BaseTask/BaseTask.bar')

    base_task.REQUIRES = MockTask
    base_task.OUTPUT = None
    base_task.OUTPUT_RENAMING = ('.foo', '.foo.bar')
    assert base_task.input().path.endswith('Name.some-file.foo')
    assert base_task.output().path.endswith('Name.some-file.foo.bar')

    base_task.SUBDIR = 'xhmm_run'
    base_task.OUTPUT = 'baz'
    assert base_task.output().path.endswith('BaseTask/xhmm_run/BaseTask.baz')

    base_task.OUTPUT = ['spam', 'eggs']
    outputs = base_task.output()
    assert outputs[0].path.endswith('BaseTask/xhmm_run/BaseTask.spam')
    assert outputs[1].path.endswith('BaseTask/xhmm_run/BaseTask.eggs')

    with pytest.raises(ValueError):
        base_task.OUTPUT = {1, 2}
        base_task.output()


def test_run_program(base_task, monkeypatch):
    # run_program uses generate_command, but we test the latter elsewhere,
    # so we just mock it here:
    def fake_generate_command(program_name, options, config):
        command = f"{program_name}"
        for key, value in options.items():
            command += f" --{key} {value}"
        return command

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

    # task.path is implemented in child classes, so we mock it here:
    def fake_path(filename):
        return '/path/to/{}'.format(filename)

    monkeypatch.setattr(paip.task_types.base_task, 'generate_command',
                        fake_generate_command)
    monkeypatch.setattr(paip.helpers, 'run_command',
                        fake_run_command)
    base_task.path = fake_path


    result = base_task.run_program(
        program_name='program',
        program_options={'foo': 'bar'},
        extra_kwarg='foo'
    )

    expected_command = 'program --foo bar --num_threads 1'
    assert result[0] == expected_command
    assert base_task.generated_command == expected_command

    args_received_by_run_command = result[1]

    # Test the command is the one that comes from generate_command
    assert args_received_by_run_command['command'] == expected_command

    # Test the logfile was created from the class name of the Task
    assert args_received_by_run_command['logfile'] == '/path/to/log.BaseTask'

    # Test extra kwargs were passed to run_command
    assert args_received_by_run_command['extra_kwarg'] == 'foo'

    # sleep_until_available_to_run.assert_called_once()


def test_find_output(base_task):
    output_files = ['foo.bar', 'bar.baz', 'qux.baz']
    output_files = [luigi.LocalTarget(fn) for fn in output_files]
    base_task.output = lambda: output_files

    assert base_task._find_output('baz').path == 'bar.baz'

    # Works with only one file in the output:
    base_task.output = lambda: output_files[0]
    assert base_task._find_output('bar').path == 'foo.bar'

    with pytest.raises(ValueError):
        base_task._find_output('nonexistent')


def test_rename_temp_bai(base_task, mock_rename):
    base_task.output = lambda: luigi.LocalTarget('out.bam')
    base_task.temp_bam = 'temp.bam'
    base_task.rename_temp_bai()
    assert mock_rename.call_args[0] == ('temp.bam.bai', 'out.bam.bai')


def test_rename_temp_idx(base_task, mock_rename):
    base_task.output = lambda: luigi.LocalTarget('out.vcf')
    base_task.temp_vcf = 'temp.vcf'
    base_task.rename_temp_idx()
    assert mock_rename.call_args[0] == ('temp.vcf.idx', 'out.vcf.idx')


def test_requires(MockTask, test_cohort_basedir):
    mock_task = MockTask(param='param-value',
                         basedir=test_cohort_basedir)

    # As single element
    mock_task.REQUIRES = MockTask
    assert mock_task.requires() == MockTask(**mock_task.param_kwargs)

    # As list
    mock_task.REQUIRES = [MockTask, MockTask]
    assert mock_task.requires() == [MockTask(**mock_task.param_kwargs),
                                    MockTask(**mock_task.param_kwargs)]

def test_running_tasks_of_this_class(MockTask, monkeypatch):
    current_tasks = [
        {'name': 'TaskName__foo1__bar__baz__30__30__123', 'status': 'RUNNING'},
        {'name': 'TaskName__foo2__bar__baz__30__30__123', 'status': 'RUNNING'},
        {'name': 'TaskName__foo3__bar__baz__30__30__123', 'status': 'RUNNING'},
    ]
    mock_status_search = MagicMock(return_value=current_tasks)
    monkeypatch.setattr(LuigiGrep, 'status_search', mock_status_search)
    MockTask.__name__ = 'TaskName'
    n = MockTask.running_tasks_of_this_class()
    assert n == 3

def test_sleep_until_available_to_run(MockTask, monkeypatch):
    # Pretend other tasks are running:
    MockTask.running_tasks_of_this_class = lambda: 2

    def fake_sleep(*args, **kwargs):
        # Now pretend that after sleeping, the other processes have finished:
        MockTask.running_tasks_of_this_class = lambda: 0
        fake_sleep.called_once = True

    fake_sleep.called_once = False
    monkeypatch.setattr(time, 'sleep', fake_sleep)

    # Check it doesn't sleep if a concurrency limit has not been set
    MockTask.MAX_CONCURRENT_TASKS = None
    MockTask.sleep_until_available_to_run()
    assert not fake_sleep.called_once

    MockTask.MAX_CONCURRENT_TASKS = 2
    MockTask.sleep_until_available_to_run()
    assert fake_sleep.called_once

