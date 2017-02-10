from os import getpid, remove
from os.path import join, isfile
from tempfile import gettempdir
from subprocess import CalledProcessError

import pytest

from paip.helpers import run_command


def test_run_command():
    stdout, stderr = run_command('echo foo')
    assert stdout == 'foo'
    assert stderr == ''

    stdout, stderr = run_command('echo foo >&2')
    assert stdout == ''
    assert stderr == 'foo'

    with pytest.raises(CalledProcessError):
        run_command('non-existent-command')


def test_log_to_file():
    logfile = join(gettempdir(), 'test_paip_{}.log'.format(getpid()))

    # Test STDOUT is logged
    run_command('echo foo', logfile=logfile)

    with open(logfile) as f:
        log_lines = [line.strip() for line in f.readlines()]

    assert 'foo' in log_lines

    # Extra checks of command running info
    assert 'echo foo' in log_lines
    assert 'Finished at' in log_lines[-2]
    assert 'Took' in log_lines[-1]

    # Test STDERR is logged correctly
    run_command('echo foo >&2', logfile=logfile, capture_stderr=True)

    with open(logfile) as f:
        log_lines = [line.strip() for line in f.readlines()]

    assert 'foo' in log_lines

    # Test STDERR is not logged
    run_command('echo foo >&2', logfile=logfile, capture_stderr=False)

    with open(logfile) as f:
        log_lines = [line.strip() for line in f.readlines()]

    assert 'foo' not in log_lines

    # Test STDOUT is not logged
    run_command('echo foo', logfile=logfile, capture_stdout=False)

    with open(logfile) as f:
        log_lines = [line.strip() for line in f.readlines()]

    assert 'foo' not in log_lines

    # Test appending
    run_command('echo foo', logfile=logfile)
    run_command('echo bar', logfile=logfile, append=True)

    with open(logfile) as f:
        log_lines = [line.strip() for line in f.readlines()]

    assert 'foo' in log_lines
    assert 'bar' in log_lines

    # Cleanup
    remove(logfile)
    assert not isfile(logfile)

