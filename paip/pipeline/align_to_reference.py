from paip.helpers import Config, path_to_resource


def align_to_reference(forward_reads, reverse_reads):
    """
    Expects two files: forward and reverse reads of the same sample.
    It will use the reference genome defined in resources.yml.

    Returns the command to align the reads to that genome.
    """
    program = 'bwa'

    command_template = Config.commands(program)
    command = command_template.format(**{
        'executable': Config.executables(program),
        'forward_reads': forward_reads,
        'reverse_reads': reverse_reads,
        'reference_genome': path_to_resource('reference_genome'),
    })

    return command

