from paip.helpers import generate_command


def realign_around_indels(input_bam, targets_file, output_bam):
    """
    Generate a command to realign the reads in the *input_bam* at the
    regions defined in *targets_file*, which will generate an *output_bam*.
    """
    program_name = 'gatk IndelRealigner'
    options = {
        'input_bam': input_bam,
        'targets_file': targets_file,
        'output_bam': output_bam,
    }

    return generate_command(program_name, options)

