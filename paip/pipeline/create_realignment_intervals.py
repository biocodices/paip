from paip.helpers import generate_command


def create_realignment_intervals(input_bam, output_file):
    """
    Generate the command that takes an *input_bam* and creates a file with
    the regions that should be realigned considering known human indels.
    """
    program_name = 'gatk RealignerTargetCreator'
    options = {
        'input_bam': input_bam,
        'output_file': output_file,
    }

    return generate_command(program_name, options)

