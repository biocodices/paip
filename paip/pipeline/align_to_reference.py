from paip.helpers import generate_command


def align_to_reference(forward_reads, reverse_reads):
    """
    Expects two files: forward and reverse reads of the same sample.
    It will use the reference genome defined in resources.yml.

    Returns the command to align the reads to that genome.
    """
    program_name = 'bwa'
    options = {
        'forward_reads': forward_reads,
        'reverse_reads': reverse_reads,
    }

    return generate_command(program_name, options)

