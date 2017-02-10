from paip.pipeline import align_to_reference


def test_align_to_reference():
    command = align_to_reference(forward_reads='./foo', reverse_reads='./bar')

    assert command == ('/path/to/bwa mem -t 8 '
                       '/path/to/human_g1k_v37.fasta '
                       './foo ./bar')

