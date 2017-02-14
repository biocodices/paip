from paip.helpers import generate_command


def create_recalibration_table(input_bam, outfile):
    """
    Given an *input_bam*, create a plain text file with a table for the
    recalibration of the scores of each called base using *outfile* as
    filename.
    """
    program_name = 'gatk BaseRecalibrator'
    options = {
        'input_bam': input_bam,
        'outfile': outfile,
    }

    return generate_command(program_name, options)

