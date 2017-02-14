from paip.pipeline import create_recalibration_table


def test_create_recalibration_table():
    command = create_recalibration_table(
        input_bam='/path/to/input_bam',
        outfile='/path/to/outfile',
    )
    assert command == ('/path/to/gatk '
                       '-T BaseRecalibrator '
                       '-nct 8 '
                       '-I /path/to/input_bam '
                       '-R /path/to/reference_genome.fasta '
                       '-L /path/to/panel_regions.bed '
                       '-knownSites /path/to/indels_1000G.vcf '
                       '-knownSites /path/to/indels_mills.vcf '
                       '-o /path/to/outfile')

