from paip.pipeline import trim_adapters


def test_trim_adapters():
    result = trim_adapters('/path/to/fwd.fastq', '/path/to/rev.fastq')

    assert result == ('/home/juan/software/ea-utils.1.1.2-537/fastq-mcf '
                      '-u -q 20 -P 33 -x 10 -l 50 '
                      '-o /path/to/fwd.trimmed.fastq '
                      '-o /path/to/rev.trimmed.fastq '
                      '/home/juan/paip_resources/illumina_adapters.fasta '
                      '/path/to/fwd.fastq '
                      '/path/to/rev.fastq')

