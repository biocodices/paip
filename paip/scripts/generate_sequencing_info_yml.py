#!/usr/bin/env python
"""
Generates a sequencing_info.yml from the fastq.gz files found in this
directory (recursively).

Usage:
    generate_sequencing_info_yml.py [--cohort-dir DIR]

Options:
    --cohort-dir DIR    Directory with the Cohort samples [default: .]
"""
import re
import yaml
from os.path import basename
from pprint import pprint
from docopt import docopt
from glob import glob
from subprocess import check_output
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict


class Sample:
    def __init__(self, name):
        self.name = name
        self.fastq_fwd = f"{self.name}/{self.name}.R1.fastq.gz"
        self.fastq_rev = f"{self.name}/{self.name}.R2.fastq.gz"
        self.instrument = self.flowcell = self.run_number = None
        self.lane_numbers = set()

    @property
    def lane_numbers_merged(self):
        return "-".join(sorted(self.lane_numbers))

    def __repr__(self):
        return f'Sample("{self.name}")'

    def seq_info(self):
        return {
            "platform": "ILLUMINA",
            "library_id": f"Lib.{self.instrument}.{self.run_number}.{self.flowcell}.{self.lane_numbers_merged}",
            "platform_unit": self.instrument,
            "run_number": self.run_number,
            "flowcell_id": self.flowcell,
            "lane_numbers_merged": self.lane_numbers_merged,
        }

    def set_data_from_read_group(self, read_group):
        # See the following link for a description of the fields in a FASTQ
        # read ID:
        #
        # http://support.illumina.com/content/dam/illumina-support/help/BaseSpaceHelp_v2/Content/Vault/Informatics/Sequencing_Analysis/BS/swSEQ_mBS_FASTQFiles.htm
        instrument, run_number, flowcell, lane_number = read_group.split(":")

        # Safety check: only ONE instrument, flowcell, and run for sample:
        if self.instrument and not instrument == self.instrument:
            raise ValueError(f"{instrument} != {self.instrument} for sample {self.name}")
        if self.flowcell and not flowcell == self.flowcell:
            raise ValueError(f"{flowcell} != {self.flowcell} for sample {self.name}")
        if self.run_number and not run_number == self.run_number:
            raise ValueError(f"{run_number} != {self.run_number} for sample {self.name}")

        self.instrument = instrument
        self.run_number = run_number
        self.flowcell = flowcell

        # I've found that exome data might have reads from the same sample
        # in more than one lane of the same flowcell. I deal with that
        # later in the pipeline, here I will just merge all the seen lanes:
        self.lane_numbers.add(lane_number)

def main(args):
    cohort_dir = args["--cohort-dir"]
    pattern = f"{cohort_dir}/*/*R?.fastq.gz" # R1.fastq.gz or R2.fastq.gz
    print(f"Trying pattern: {pattern}")

    sample_names = {re.sub(r"\.R[12]\.fastq\.gz", "", basename(fastq))
                    for fastq in glob(pattern)}
    samples = {name: Sample(name) for name in sample_names}

    print(f"Found samples: {', '.join(sample_names)}")
    print(f"Will process FASTQ files from {len(samples)} samples and extract "
          "their sequencing info from the read IDs:\n")

    with ProcessPoolExecutor() as executor:
        future_to_sample_name = {}
        for sample in samples.values():
            future = executor.submit(extract_read_groups, sample.fastq_fwd)
            future_to_sample_name[future] = sample.name
            future = executor.submit(extract_read_groups, sample.fastq_rev)
            future_to_sample_name[future] = sample.name

        for future in as_completed(future_to_sample_name):
            sample_name = future_to_sample_name[future]
            sample = samples[sample_name]

            # Here I call "read groups" to unique combinations of
            # instrument:run_number:flowcell:lane seen in the fastq IDs
            seen_read_groups_for_this_sample = future.result()
            for read_group in seen_read_groups_for_this_sample:
                sample.set_data_from_read_group(read_group.lstrip("@"))

            print(sample.name)
            pprint(sample.seq_info())
            print()

    seq_info = {sample.name: sample.seq_info() for sample in samples.values()}
    fn = "sequencing_data.yml"
    with open(fn, "w") as f:
        yaml.dump(seq_info, f, default_flow_style=False)
    print(f"Written to: {fn}")


def extract_read_groups(path):
    """
    Read IDs have this format:

        @<instrument>:<run number>:<flowcell ID>:<lane>:<tile>:<x-pos>:<y-pos>
        <read>:<is filtered>:<control number>:<sample number>

    Extract the unique values of the first four fields in a FASTQ file, which
    is what we will use as read groups, and how many reads had each.

    There's a side effect as well: "| tee {rg_file}" will produce a file
    with the unique read groups.
    """
    rg_file = path.replace(".fastq.gz", ".unique_read_groups")
    command = f"zgrep '^@' {path} | cut -d: -f1-4 | uniq -c | tee {rg_file}"
    print(command)
    result = check_output(command, shell=True).decode().strip()

    # This command might have many lines, if there are different read groups
    # of instrument-run-flowcell-lane in the FASTQ file:
    lines = result.split("\n")
    read_groups_with_read_counts = {}
    for line in lines:
        match = re.search(r"(?P<count>.+)\s+(?P<rg>.+)", line)
        read_group = match.group("rg").lstrip("@")
        count = int(match.group("count"))
        read_groups_with_read_counts[read_group] = count

    print(f"{path}:\n{read_groups_with_read_counts}\n")

    # Don't return the counts, just the read group names:
    return list(read_groups_with_read_counts.keys())


if __name__ == "__main__":
    args = docopt(__doc__)
    main(args)
