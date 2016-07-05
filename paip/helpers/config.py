import yaml
from os.path import join, expanduser


def read_config(filename):
    base_dir = expanduser('~/.paip')
    return yaml.load(open(join(base_dir, filename + '.yml')))


class Config:
    def __new__(self, config_label):
        """
        Expects a ~/.paip dir with yml config files in it.
        Call directly Config(config_label) to get a dictionary with settings.
        """
        return read_config(config_label)

    params = read_config('parameters')
    executables = read_config('executables')
