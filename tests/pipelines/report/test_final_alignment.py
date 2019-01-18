from paip.pipelines.report import FinalAlignment
from paip.pipelines.ion_torrent import ReheaderBam
from paip.pipelines.variant_calling import MarkDuplicates


def test_requires_and_output(sample_task_factory):
    ion_task = sample_task_factory(FinalAlignment,
                                   cohort_name='IonCohort',
                                   sample_name='Sample1')

    assert isinstance(ion_task.requires(), ReheaderBam)
    assert ion_task.output().path.endswith('Sample1.fix.bam')

    illumina_task = sample_task_factory(FinalAlignment,
                                        cohort_name='Cohort1',
                                        sample_name='Sample1')

    assert isinstance(illumina_task.requires(), MarkDuplicates)
    assert illumina_task.output().path.endswith('Sample1.dupmarked_alignment.bam')
