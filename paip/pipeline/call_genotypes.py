from paip.task_types import SampleTask
from paip.pipeline import CallTargets, CallVariants


class CallGenotypes(SampleTask):
    """
    Wrapper Task to run both CallVariants and CallTargets.
    """
    def requires(self):
        yield CallTargets(self.sample)
        yield CallVariants(self.sample)

