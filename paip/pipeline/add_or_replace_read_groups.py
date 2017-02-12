from paip.helpers import generate_command


def add_or_replace_read_groups(sam_path, sample_id, library_id,
                               sequencing_id, platform, platform_unit,
                               out_path):
    """
    Given data about the sample and sequencing, return a command to
    add or replace the read groups in a SAM file and to create a BAM
    file with the new read groups for each read.
    """
    program_name = 'picard AddOrReplaceReadGroups'
    options = {
        'input_samfile': sam_path,
        'sequencing_id': sequencing_id,
        'library_id': library_id,
        'sample_id': sample_id,
        'platform': platform,
        'platform_unit': platform_unit,
        'output_bamfile': out_path,
    }

    return generate_command(program_name, options)

