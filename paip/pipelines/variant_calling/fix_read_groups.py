import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import AlignToReferenceAndAddReadGroup
from paip.helpers import fix_sam_read_groups
from paip.helpers.create_cohort_task import create_cohort_task


class FixReadGroups(SampleTask):
    """
    Takes the SAM that BWA outputs, which has a single @RG entry for read group
    with the merged lane numbers in the ID: part, for instance:

        @RG     ID:INSTRUMENT.RUN.FLOWCELL.1-2-3    LB:Lib    PL:ILLUMINA ...

    This task fixes the header producing separate @RG entries for each lane
    number seen, and fixes the RG: part of each single read in the file with
    the corresponding lane-number-based read group inferred from the read
    ID (this takes some time, since it loops over all SAM lines).
    """
    REQUIRES = AlignToReferenceAndAddReadGroup

    def run(self):
        with self.output().temporary_path() as tmp_out:
            fix_sam_read_groups(sam_input=self.input().path,
                                out_path=tmp_out)

    def output(self):
        path = self.input().path.replace('.wrong_rg.', '.fixed_rg.')
        return luigi.LocalTarget(path)


FixReadGroupsCohort = create_cohort_task(FixReadGroups)
