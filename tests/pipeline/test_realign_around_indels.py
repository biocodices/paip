from paip.pipeline import realign_around_indels


def test_realign_around_indels():
    command = realign_around_indels(
        input_bam='/path/to/input_bam',
        targets_file='/path/to/target_intervals',
        output_bam='/path/to/output_bam',
    )

    assert command == ('/path/to/gatk -T IndelRealigner '
                       '-I /path/to/input_bam '
                       '-R /path/to/reference_genome.fasta '
                       '-targetIntervals /path/to/target_intervals '
                       '-o /path/to/output_bam')

