import pytest

from paip.pipelines.variant_calling import JointGenotyping, MakeGVCF


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(JointGenotyping)


def test_requires(task):
    expected_dependencies = [MakeGVCF(sample='Sample1', basedir=task.basedir),
                             MakeGVCF(sample='Sample2', basedir=task.basedir)]
    assert task.requires() == expected_dependencies


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 GenotypeGVCFs variant_sites'
    expected_inputs = ['-V {}'.format(input_[0].path) for input_ in task.input()]
    assert program_options['input_gvcfs'] == ' '.join(expected_inputs)
    assert 'vcf-luigi-tmp' in program_options['output_vcf']
    assert mock_rename.call_count == 2

