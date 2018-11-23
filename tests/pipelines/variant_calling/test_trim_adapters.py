from paip.pipelines.variant_calling import TrimAdapters


def test_run(sample_task_factory):
    task = sample_task_factory(TrimAdapters)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'cutadapt'
    assert program_options['forward_reads'] == task.input()['forward_reads'].path
    assert program_options['reverse_reads'] == task.input()['reverse_reads'].path
    assert 'R1.trimmed.fastq.gz' in program_options['forward_output']
    assert 'R2.trimmed.fastq.gz' in program_options['reverse_output']

    # This is important: cutadapt will only compress its output if it detects
    # filenames ending in ".gz", so we can't use different endings:
    assert program_options['forward_output'].endswith('.gz')
    assert program_options['reverse_output'].endswith('.gz')
