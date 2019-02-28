from os import getpid, remove
from os.path import join, isfile
from tempfile import gettempdir
from subprocess import CalledProcessError

import pytest

from paip.helpers import run_command


def read_lines_from_file(path):
    with open(path) as f:
        lines = [line.strip() for line in f]
    return lines


def test_run_command():
    stdout, stderr = run_command('echo foo')
    assert stdout == b'foo\n'
    assert stderr == b''

    stdout, stderr = run_command('echo foo >&2')
    assert stdout == b''
    assert stderr == b'foo\n'


def test_raises(caplog):
    with pytest.raises(CalledProcessError):
        run_command('non-existent-command')

    records = [record.message for record in caplog.records]
    assert 'This command failed (return code=127):\nnon-existent-command' in records
    assert 'STDERR:\n/bin/sh: 1: non-existent-command: not found' in records


def test_log_to_file():
    logfile = join(gettempdir(), 'test_paip_{}.log'.format(getpid()))

    # Test STDOUT is logged
    run_command('echo foo', logfile=logfile)
    log_lines = read_lines_from_file(logfile)
    assert 'foo' in log_lines

    # Extra checks of command running info
    log_lines = read_lines_from_file(logfile)
    assert '—————————— START' in log_lines
    assert '—————————— COMMAND' in log_lines
    assert 'echo foo' in log_lines
    assert '—————————— STDOUT' in log_lines
    assert '—————————— STDERR' in log_lines
    assert '—————————— END' in log_lines
    assert 'Took' in log_lines[-2]

    # Test STDERR is logged correctly
    run_command('echo foo >&2', logfile=logfile, log_stderr=True)

    assert 'foo' in read_lines_from_file(logfile)

    # Test STDERR is not logged
    run_command('echo foo >&2', logfile=logfile, log_stderr=False)

    assert 'foo' not in read_lines_from_file(logfile)

    # Test STDOUT is not logged
    run_command('echo foo', logfile=logfile, log_stdout=False)

    assert 'foo' not in read_lines_from_file(logfile)

    # Test appending
    run_command('echo foo', logfile=logfile)
    run_command('echo bar', logfile=logfile, log_append=True)

    assert 'foo' in read_lines_from_file(logfile)
    assert 'bar' in read_lines_from_file(logfile)

    # Cleanup
    remove(logfile)
    assert not isfile(logfile)


def test_redirect_output_to_file():
    outfile = join(gettempdir(), 'test_paip_{}.outfile.txt'.format(getpid()))
    run_command('echo foo', redirect_stdout_to_path=outfile)
    assert 'foo' in read_lines_from_file(outfile)

    # Cleanup
    remove(outfile)
