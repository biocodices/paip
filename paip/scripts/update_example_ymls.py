#!/usr/bin/env python3.5

from os.path import expanduser, dirname, abspath, join
from shutil import copy


#######################################################################
#                                                                     #
# Use this script to update the config files in paip/example_config/  #
# with your own config files located in ~/.paip/                      #
#                                                                     #
#######################################################################


config_files = [
    '~/.paip/resources.yml',
    '~/.paip/commands.yml',
    '~/.paip/executables.yml',
]

package_dir = dirname(dirname(abspath(__file__)))
examples_dir = join(package_dir, 'example_config')

for config_file in config_files:
    config_file = expanduser(config_file)
    print('copy: {} -> {}'.format(config_file, examples_dir))
    copy(config_file, examples_dir)

