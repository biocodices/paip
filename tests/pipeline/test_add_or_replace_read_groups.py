from paip.pipeline import add_or_replace_read_groups


def test_add_or_replace_read_groups():
    command = add_or_replace_read_groups(
        sam_path='/path/to/infile.sam',
        sample_id='Spl1',
        library_id='Lib1',
        sequencing_id='Seq1',
        platform='Platform',
        platform_unit='PlatUnit',
        out_path='/path/to/outfile.bam'
    )

    assert command == (
        '/path/to/picard AddOrReplaceReadGroups '
        'I=/path/to/infile.sam '
        'ID=Seq1.Lib1.PlatUnit.Spl1 '
        'SM=Spl1 '
        'LB=Lib1 '
        'PL=Platform '
        'PU=PlatUnit '
        'O=/path/to/outfile.bam '
        'SO=coordinate '
        'CREATE_INDEX=True '
        'VALIDATION_STRINGENCY=LENIENT'
    )

