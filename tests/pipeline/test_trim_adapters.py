from paip.pipeline import trim_adapters


def test_trim_adapters():
    command = trim_adapters('/path/to/fwd.fastq', '/path/to/rev.fastq')

    assert command == ('/path/to/fastq-mcf '
                       '-u -q 20 -P 33 -x 10 -l 50 '
                       '-o /path/to/fwd.trimmed.fastq '
                       '-o /path/to/rev.trimmed.fastq '
                       '/path/to/illumina_adapters.fasta '
                       '/path/to/fwd.fastq '
                       '/path/to/rev.fastq')

