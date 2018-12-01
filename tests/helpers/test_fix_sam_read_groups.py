from os import remove, getpid
from os.path import isfile, join
from tempfile import gettempdir
import pytest

from paip.helpers import fix_sam_read_groups


def test_fix_sam_read_groups():
    sam_input = pytest.helpers.file('wrong_read_groups.sam')
    sam_output = join(gettempdir(), f'test_paip_{getpid()}.fixed_rg.sam')
    sam_output_expected = pytest.helpers.file('fixed_read_groups.expected.sam')

    result = fix_sam_read_groups(sam_input, out_path=sam_output)

    # The input SAM has only one read group @RG in the header
    # but three different "inferable" read groups from the read IDs.

    # We expect the new header to have two extra @RG entries
    # And some reads to have a modified RG: field

    assert isfile(sam_output)

    with open(sam_output) as f1, open(sam_output_expected) as f2:
        new_lines = [line.strip() for line in f1]
        expected_new_lines = [line.strip() for line in f2]

    for new_line, expected_new_line in zip(new_lines, expected_new_lines):
        assert new_line == expected_new_line

    # Cleanup
    remove(sam_output)
    assert not isfile(sam_output)
