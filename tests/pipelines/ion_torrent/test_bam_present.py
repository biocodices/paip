from paip.pipelines.ion_torrent import BamPresent


def test_bam_present(sample_task_factory):
    task = sample_task_factory(BamPresent,
                               sample_name='Sample1',
                               cohort_name='IonCohort')
    assert task.complete()

    task = sample_task_factory(BamPresent,
                               sample_name='SampleWithoutBAM',
                               cohort_name='IonCohort')

    assert not task.complete()
