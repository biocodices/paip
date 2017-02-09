from os.path import join
from paip.helpers.config import Config


def available_resources():
    return Config('resources')


def path_to_resource(label):
    """
    Assuming you defined 'base_dir' and the *label* in the resources.yml file,
    this methos will join them and return the path, like:

        > Resource.path_to('reference_genome')
            # => /home/jdoe/resources/human_genome.fasta

        > Resource.path_to('illumina_adapters')
            # => /home/jdoe/resources/illumina_adps.fasta

    You can query a deep key from the YAML by separating nested keys with a ':',
    for instance:

        > Resource.path_to('indels:1000G')
    """
    resources = Config.resources()
    base_dir = resources['base_dir']

    # Hack to do the nested lookups in the dict:
    value = resources  # Top level
    for key in label.split(':'):
        if not isinstance(value, dict):
            raise TypeError('Key before "{}" in "{}" does not hold a dictionary'
                            .format(key, label))

        value = value[key]  # Gets one level deeper each time

    return join(base_dir, value)

