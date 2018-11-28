import os
import re
from subprocess import run

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

    if os.path.isfile(out_path):
        os.remove(out_path)

    assert '.sam' in out_path # accepts files like "myfile.sam-luigi-tmp-1234"

    sam_header_path = out_path.replace('.sam', '.header.sam')
    sam_body_path = out_path.replace('.sam', '.no-header.sam')

    # Write the header # FIXME: it still lacks the new @RG entriies

    regex_id = re.compile(r'^(.+?:.+?:.+?:.+?):.+?:.+?:.+?\s')
    regex_rg = re.compile(r'\sRG:Z:(.+)\s')

    # Write the body of the SAM, fixing read groups read by read:

    inferred_read_groups = set()

    with open(sam_input) as f_in, open(sam_body_path, 'w') as f_out:
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

    # Write the header of the SAM, adding an @RG entry for each read group
    # seen among the reads:

    #
    #
    #
    # FIXME: SEGUIR Con esto pero tomar los read groups del archivo
    # unique_read_groups que antes hice y escribir PRIMERO el header!
    # única manera de que luego no tenga que concatenar y tener tres
    # copias de todo el cuerpo del SAM en el disco en simultáneo
    #
    # O MEJORRRRRRRR: asumir que en el ** único ** read group que vino de
    # BWA en el header, los lanes están mergeados! 3-4
    #
    #
    #

    header_lines = []
    with open(sam_input) as f_in:
        for line in f_in:
            if not line.startswith("@"): # When the header is over
                break
            header_lines.append(line)

    header_without_RG = [l for l in header_lines if not l.startswith('@RG')]
    header_RG = [l for l in header_lines if l.startswith('@RG')]
    template_RG_line = header_RG[0]

    rg_lines = []
    for read_group in sorted(inferred_read_groups):
        rg_line = re.sub(r'(ID:)(.+?)(\s.+)', rf'\1{read_group}\3',
                         template_RG_line)
        rg_lines.append(rg_line)

    with open(sam_header_path, 'w') as f_out:
        for header_line in header_without_RG + rg_lines:
            f_out.write(header_line)
