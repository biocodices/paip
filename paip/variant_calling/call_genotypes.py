from paip.task_types import SampleTask
from paip.variant_calling import CallTargets, MakeGVCF


class CallGenotypes(SampleTask):
    """
    Wrapper Task to run both CallVariants and CallTargets.
    """
    def requires(self):
        yield CallTargets(self.sample)
        yield MakeGVCF(self.sample)

