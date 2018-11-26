#!/usr/bin/env python
"""
Generates a sequencing_info.yml from the fastq.gz files found in this
directory (recursively).

Usage:
    generate_sequencing_info_yml.py --cohort-dir DIR

Options:
    --cohort-dir DIR    Directory with the Cohort samples.
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
        self.instrument = self.flowcell = self.run = None

    def __repr__(self):
        return f'Sample("{self.name}")'

    def seq_info(self):
        return {
            "library_id": f"Lib-{self.instrument}-{self.run}",
            "sequencing_id": f"NGS-{self.instrument}-{self.run}",
            "platform": "Illumina",
            "platform_unit": self.instrument,
            "flowcell_id": self.flowcell,
            "lane_number": self.lane_number,
        }

    def set_instrument_run_flowcell_lane(self, instrument, run, flowcell, lane_number):
        if self.instrument and not instrument == self.instrument:
            raise ValueError(f"{instrument} != {self.instrument} for sample {self.name}")
        if self.flowcell and not flowcell == self.flowcell:
            raise ValueError(f"{flowcell} != {self.flowcell} for sample {self.name}")
        if self.run and not run == self.run:
            raise ValueError(f"{run} != {self.run} for sample {self.name}")

        self.instrument = instrument
        self.run = run
        self.flowcell = flowcell
        self.lane_number = lane_number

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
            future = executor.submit(extract_instrument_run_flowcell_lane, sample.fastq_fwd)
            future_to_sample_name[future] = sample.name
            future = executor.submit(extract_instrument_run_flowcell_lane, sample.fastq_rev)
            future_to_sample_name[future] = sample.name

        for future in as_completed(future_to_sample_name):
            sample_name = future_to_sample_name[future]
            instrument, run, flowcell, lane = future.result()
            sample = samples[sample_name]
            sample.set_instrument_run_flowcell_lane(instrument, run, flowcell, lane)

            print(sample.name)
            pprint(sample.seq_info())
            print()

    seq_info = {sample.name: sample.seq_info() for sample in samples.values()}
    fn = "sequencing_data.yml"
    with open(fn, "w") as f:
        yaml.dump(seq_info, f, default_flow_style=False)
    print(f"Written to: {fn}")


def extract_instrument_run_flowcell_lane(path):
    """
    Read IDs have this format:

        @<instrument>:<run number>:<flowcell ID>:<lane>:<tile>:<x-pos>:<y-pos>
        <read>:<is filtered>:<control number>:<sample number>

    Extract the unique values of the first four fields in a FASTQ file.
    """
    command = f"zcat {path} | grep '^@' | cut -d: -f1-4 | uniq"
    print(command)
    result = check_output(command, shell=True).decode().strip()
    return result.lstrip("@").split(":")


if __name__ == "__main__":
    args = docopt(__doc__)
    main(args)
