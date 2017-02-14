from paip.helpers import generate_command


def trim_adapters(forward_reads, reverse_reads):
    """
    Expects two filepaths: forward and reverse .fastq files of the same
    sample. It will search for an adapters file defined in resources.yml.

    Returns the command to trim the adapters of those reads files.
    """
    program_name = 'fastq-mcf'
    options = {
        'forward_reads': forward_reads,
        'reverse_reads': reverse_reads,
        'forward_output': forward_reads.replace('.fastq', '.trimmed.fastq'),
        'reverse_output': reverse_reads.replace('.fastq', '.trimmed.fastq'),
    }

    return generate_command(program_name, options)

