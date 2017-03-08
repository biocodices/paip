import pytest

from paip.pipelines.quality_control import VariantEval


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(VariantEval,
                               extra_params={'pipeline_type': 'variant_sites'})


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk VariantEval'
    assert program_options['input_vcf'] == task.input().fn
    assert 'eval.grp-luigi-tmp' in program_options['output_file']

