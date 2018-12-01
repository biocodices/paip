import os

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import (
    AlignToReferenceAndAddReadGroup,
    FixReadGroups,
)
from paip.helpers.create_cohort_task import create_cohort_task


class DeleteSamFiles(SampleTask):
    """
    Remove the SAM files from the input tasks to save disk space.
    """
    REQUIRES = {
        'wrong_rg_alignment': AlignToReferenceAndAddReadGroup,
        'fixed_rg_alignment': FixReadGroups,
    }

    def run(self):
        os.remove(self.input()['wrong_rg_alignment'].path)
        os.remove(self.input()['fixed_rg_alignment'].path)

    def complete(self):
        f1 = self.input()['wrong_rg_alignment'].path
        f2 = self.input()['fixed_rg_alignment'].path
        return not os.path.isfile(f1) and not os.path.isfile(f2)


DeleteSamFilesCohort = create_cohort_task(DeleteSamFiles)
