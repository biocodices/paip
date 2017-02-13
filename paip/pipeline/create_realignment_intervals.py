from paip.helpers import (
    path_to_resource,
    generate_command,
)


def create_realignment_intervals(input_bamfile, output_file):
    """
    Generate the command that takes an *input_bamfile* and creates a file with
    the regions that should be realigned considering known human indels.
    """
    program_name = 'gatk RealignerTargetCreator'
    options = {
        'input_bamfile': input_bamfile,
        'reference_genome': path_to_resource('reference_genome'),
        'panel_regions': path_to_resource('panel_regions'),
        'output_file': output_file,
        'indels_1kG': path_to_resource('indels_1000G'),
        'indels_mills': path_to_resource('indels_mills'),
    }

    return generate_command(program_name, options)

