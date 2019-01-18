import luigi

from paip.task_types import SampleTask
from paip.pipelines.ion_torrent import ReheaderBam
from paip.pipelines.variant_calling import MarkDuplicates


class FinalAlignment(SampleTask, luigi.WrapperTask):
    """
    Wrapper task to get the last/definitive alignment file for reports and
    analysis.
    """
    def requires(self):
        if self.ion:
            return ReheaderBam(**self.param_kwargs)
        else:
            return MarkDuplicates(**self.param_kwargs)

    def output(self):
        if self.ion:
            alignment_target = self.input()
        else:
            alignment_target = self.input()['dupmarked_bam']

        return alignment_target
