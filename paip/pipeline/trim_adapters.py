from paip.helpers import Config, path_to_resource


def trim_adapters(forward_reads, reverse_reads):
    """
    Expects two filepaths: forward and reverse .fastq files of the same
    sample. It will search for an adapters file defined in resources.yml.

    Returns the command to trim the adapters of those reads files.
    """
    program = 'fastq-mcf'

    command_template = Config.commands(program)
    command = command_template.format(**{
        'executable': Config.executables(program),
        'forward_reads': forward_reads,
        'reverse_reads': reverse_reads,
        'forward_output': forward_reads.replace('.fastq', '.trimmed.fastq'),
        'reverse_output': reverse_reads.replace('.fastq', '.trimmed.fastq'),
        'adapters': path_to_resource('illumina_adapters'),
    })

    return command

