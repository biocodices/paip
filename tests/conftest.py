from os.path import join, dirname

pytest_plugins = ['helpers_namespace']

import pytest


@pytest.helpers.register
def test_file(filename):
    """Return the path to a file/dir under this repo's tests/files."""
    return join(dirname(__file__), 'files', filename)

