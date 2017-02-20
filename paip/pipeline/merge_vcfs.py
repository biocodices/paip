import luigi

from paip.task_types import CohortTask
from paip.pipeline import CallTargets


class MergeVcfs(CohortTask):
    """
    Take the single-sample VCF files from each sample in the target-sites
    pipeline and merge them into a multi-sample VCF.
    """
    def requires(self):
        return [CallTargets(sample) for sample in self.sample_list]

    def run(self):
        pass

    def output(self):
        fn = 'target_sites.raw_genotypes.vcf'
        return luigi.LocalTarget(self.cohort_path(fn))

