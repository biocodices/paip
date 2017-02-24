from paip.task_types import CohortTask
from paip.pipeline import ExtractSample


class SplitMultisampleVCF(CohortTask):
    """
    Takes a multi-sample VCF and generates a new VCF for each sample in the
    cohort.
    """
    def requires(self):
        for sample in self.sample_list:
            yield ExtractSample(sample=sample, **self.param_kwargs)

