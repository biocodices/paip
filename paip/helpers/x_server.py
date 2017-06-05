import subprocess
from contextlib import contextmanager


@contextmanager
def X_server(screen_number):
    """
    Starts an X server with Xvfb in the passed *screen_number* and
    kills it on exit.
    """
    command_arguments = ['Xvfb', ':{}'.format(screen_number)]
    xvfb = subprocess.Popen(command_arguments)

    yield screen_number

    xvfb.kill()

