from paip.pipeline import align_to_reference


def test_align_to_reference():
    command = align_to_reference(forward_reads='./fwd.fastq',
                                 reverse_reads='./rev.fastq')

    assert command == ('/path/to/bwa mem -t 8 '
                       '/path/to/reference_genome.fasta '
                       './fwd.fastq ./rev.fastq')

