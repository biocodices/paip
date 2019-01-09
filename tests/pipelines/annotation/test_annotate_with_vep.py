import re

from paip.pipelines.annotation import AnnotateWithVep


def test_run(cohort_task_factory):
    task = cohort_task_factory(AnnotateWithVep,
                               cohort_name='Cohort1')
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'vep' in command
    assert re.search(r'--dir .+/vep_data', command)
    assert re.search(r'--dir_cache .+/vep_data', command)
    assert re.search(r'--dir_plugins .+/vep_data', command)
    assert re.search(r'--species homo_sapiens', command)
    assert re.search(r'--assembly GRCh37', command)
    assert re.search(r'--stats_file .+/Cohort1/Cohort1..+.summary.html', command)
    assert re.search(r'--format vcf', command)
    assert re.search(r'--everything', command)
    assert re.search(r'--offline', command)
    assert re.search(r'-i .+/Cohort1/Cohort1..+.vcf', command)
    assert re.search(r'-o .+/Cohort1/Cohort1..+.vep.vcf-luigi-tmp-.+', command)
