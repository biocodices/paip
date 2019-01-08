from paip.task_types import SampleTask
from paip.pipelines.ion_torrent import BamPresent
from paip.helpers.create_cohort_task import create_cohort_task


class ReheaderBam(SampleTask):
    """
    Expects a raw BAM from IonTorrent and fixes several things in the header
    that give problems downstream:

      - The length of chrM, which does not match UCSC hg19 reference.
      - External name under the "SM:" tag, which does not match our sample name.
    """
    REQUIRES = BamPresent
    OUTPUT = 'fix.bam'

    def run(self):
        header_sam = self.input().path.replace('.bam', '.header.sam')
        header_sam_fixed = header_sam.replace('.sam', '.fix.sam')

        self.run_program('samtools extract header',
                         {'input_bam': self.input().path},
                         redirect_stdout_to_path=header_sam)

        self.fix_header_sam(header_sam, header_sam_fixed)

        with self.output().temporary_path() as temp_bam:
            self.run_program('samtools reheader',
                             {'input_bam': self.input().path,
                              'header_sam': header_sam_fixed},
                              redirect_stdout_to_path=temp_bam)

    def fix_header_sam(self, in_header, out_header):
        """
        Fix input *header_sam* and write the result to *out_header_sam*.
        """
        with open(in_header) as f1, open(out_header, 'w') as f2:
            for line in f1:
                fixed_line = line

                # Remove mithocondrial contig
                if 'chrM' in line:
                    continue
                    # This might cause trouble in the future if some read is
                    # mapped to the chrM accidentally.
                    # The right way to get rid of the problem is to filter the
                    # input ion.bam by the regions with samtools -L BED (TODO)

                # Fix contig names chr1 -> 1
                if 'SN:chr' in line:
                    fixed_line = fixed_line.replace('SN:chr', 'SN:')

                # Fix sample name
                if line.startswith('@RG'):
                    # fields = [f for f in re.split(r"\s+", line) if f]
                    fields = line.split("\t")
                    fixed_fields = [f'SM:{self.name}' if 'SM:' in f else f
                                    for f in fields]

                    fixed_line = "\t".join(fixed_fields)

                    if not fixed_line.endswith("\n"):
                        # If SM: is the *last* field, we're removing the
                        # trailing newline in the previous fix, so we need
                        # to restore it:
                        fixed_line += "\n"

                f2.write(fixed_line)


ReheaderBamCohort = create_cohort_task(ReheaderBam)
