import os
import re
from subprocess import run

from more_itertools import collapse, unique_everseen, one
from tqdm import tqdm


def fix_sam_read_groups(sam_input, out_path, progress_bar=False):
    """
    This was written to deal with the result of read group tagging by BWA.
    The produced SAM has a single read group in the header, under a line like:

        @RG  ID:PLTF.RUN.FLOWCELL.LANE1  LB:LB  PL:ILLUMINA  PU:PU  SM:SM

    But then reads might come from different lanes than LANE1, which can be
    seen in the Illumina read IDs:

        PLTF:RUN:FLOWCELL:LANE1:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE1
        PLTF:RUN:FLOWCELL:LANE1:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE1
        PLTF:RUN:FLOWCELL:LANE2:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE1 <- :(
        PLTF:RUN:FLOWCELL:LANE2:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE1 <- :(

    The idea is to produce a new SAM fixing this situation in two ways:

    - The header of the new SAM must have a new @RG line for each different
        read group inferred from the read IDs. In this case:

        @RG  ID:PLTF.RUN.FLOWCELL.LANE1  LB:LB  PL:ILLUMINA  PU:PU  SM:SM
        @RG  ID:PLTF.RUN.FLOWCELL.LANE2  LB:LB  PL:ILLUMINA  PU:PU  SM:SM

    - The read group assigned to each read in the RG:Z: tag should match
      its true read grop, inferred from the first fields of the read ID:

        PLTF:RUN:FLOWCELL:LANE1:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE1
        PLTF:RUN:FLOWCELL:LANE1:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE1
        PLTF:RUN:FLOWCELL:LANE2:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE2 <- ok
        PLTF:RUN:FLOWCELL:LANE2:X:Y:FOO ... RG:Z:PLTF:RUN:FLOWCELL:LANE2 <- ok

    Returns the path to the new SAM produced with those fixes.
    """
    # NOTE: the SAM files will be HEAVY, specially for exome data (say, 20Gb,
    # 50 million lines).

    #  if os.path.isfile(out_path):
        #  os.remove(out_path)

    assert '.sam' in out_path # accepts files like "myfile.sam-luigi-tmp-1234"

    # Write the header of the new SAM, with one @RG entry for each lane

    headers = []
    with open(sam_input) as f_in:
        for line in f_in:
            if not line.startswith("@"): # When the header is over
                break
            headers.append(line)

    headers_not_RG = [l for l in headers if not l.startswith('@RG')]
    headers_RG = [l for l in headers if l.startswith('@RG')]

    # This entire function assumes the following structure for read group IDs:
    # INSTRUMENT.RUN.FLOWCELL.1-2-3
    # where 1-2-3 are the merged lane numbers
    lane_numbers = []
    for RG_line in headers_RG:
        RG_header_parts = RG_line.split('\t')
        # [@RG, ID:INSTRUMENT.RUN.FLOWCELL.1-2-3, LB:LIB, PL:ILLUMINA, ...]

        RG_ID = one(chunk for chunk in RG_header_parts if 'ID:' in chunk)
        # ID:INSTRUMENT.RUN.FLOWCELL.1-2-3

        lane_numbers_merged = RG_ID.split('.')[-1] # 1-2-3

        for lane_number in lane_numbers_merged.split('-'): # [1, 2, 3]
            lane_numbers.append(lane_number)

    # One RG line for each lane number seen:
    new_RG_headers = []
    template_RG_line = headers_RG[0]
    for lane_number in sorted(unique_everseen(lane_numbers)):
        new_RG_header = re.sub(r'(ID:)(.+?\.)(.+?\.)(.+?\.)(.+?)(\s)',
                               rf'\1\2\3\g<4>{lane_number}\6',
                               template_RG_line)
        new_RG_headers.append(new_RG_header)

    with open(out_path, 'w') as f_out:
        for header in headers_not_RG + new_RG_headers:
            f_out.write(header)

    # Write the body of the SAM, fixing read groups read by read:

    regex_id = re.compile(r'^(.+?:.+?:.+?:.+?):.+?:.+?:.+?\s')
    regex_rg = re.compile(r'\sRG:Z:(.+)\s')

    inferred_read_groups = set()

    with open(sam_input) as f_in, open(out_path, 'a') as f_out:
        input_iterable = tqdm(f_in) if progress_bar else f_in

        # NOTE: this will loop over ~50M lines for exome data!
        for line in input_iterable:
            if line.startswith('@'):
                continue
            fixed_line = line
            match_id = regex_id.match(line)
            match_rg = regex_rg.search(line)
            inferred_read_group = match_id.group(1).replace(':', '.')
            seen_read_group = match_rg.group(1)
            if seen_read_group != inferred_read_group:
                fixed_line = fixed_line.replace(seen_read_group,
                                                inferred_read_group)
            inferred_read_groups.add(inferred_read_group)
            f_out.write(fixed_line)

    return out_path
