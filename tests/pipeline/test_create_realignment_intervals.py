from paip.pipeline import create_realignment_intervals


def test_create_realignment_intervals():
    command = create_realignment_intervals(
        input_bam='/path/to/bamfile',
        output_file='/path/to/outfile',
    )

    assert command == ('/path/to/gatk -T RealignerTargetCreator '
                       '-I /path/to/bamfile '
                       '-R /path/to/reference_genome.fasta '
                       '-known /path/to/indels_1000G.vcf '
                       '-known /path/to/indels_mills.vcf '
                       '-L /path/to/panel_regions.bed '
                       '-o /path/to/outfile')

