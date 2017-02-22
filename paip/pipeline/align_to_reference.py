from paip.task_types import SampleTask
from paip.pipeline import TrimAdapters


class AlignToReference(SampleTask):
    """
    Expects two files: forward and reverse reads of the same sample.
    It will use the reference genome defined in resources.yml to
    map the genes to genomic coordinates.

    Generates a .sam file with the raw alignments.
    """
    REQUIRES = TrimAdapters
    OUTPUT = 'raw_alignment.sam'

    def run(self):
        program_options = {
            'forward_reads': self.input()[0].fn,
            'reverse_reads': self.input()[1].fn,
        }

        # BWA writes the aligned reads to STDOUT, so we capture that:
        stdout, _ = self.run_program('bwa', program_options, log_stdout=False)

        # And then we write it to the output file:
        with open(self.output().fn, 'wb') as f:
            f.write(stdout)

