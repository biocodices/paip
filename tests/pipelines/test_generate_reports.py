from unittest.mock import mock_open, patch, MagicMock

import pytest

from paip.pipelines.generate_reports import GenerateReports
import paip.pipelines.generate_reports


extra_params = {
    'vep_tsv': 'vep.tsv',
    'genes_json': 'genes.json',
    'variants_json': 'variants.json',

    'templates_dir': '/path/to/templates',
    'translations_dir': '/path/to/translations',

    'min_reportable_category': 'CATEGORY',
    'min_odds_ratio': 1.5,
    'max_frequency': 0.5,
}


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(GenerateReports,
                               extra_params=extra_params)


def test_run(task, monkeypatch):
    # Mock the ReportsPipeline class so it returns a mocked instance:
    pipeline_instance = MagicMock()
    ReportsPipeline = MagicMock(return_value=pipeline_instance)
    monkeypatch.setattr(paip.pipelines.generate_reports,
                        'ReportsPipeline', ReportsPipeline)

    open_ = mock_open()
    with patch('paip.pipelines.generate_reports.open', open_):
        task.run()

    # Check the reports generator has been called with the correct arguments

    assert ReportsPipeline.call_count == 1

    init_args = ReportsPipeline.call_args[1]

    for param_name, param_value in extra_params.items():
        assert init_args[param_name] == param_value

    assert init_args['genotypes_vcf'] == \
        pytest.helpers.file('Cohort1/Sample1/Sample1.reportable.eff.vcf')
    assert init_args['outdir'] == \
        pytest.helpers.file('Cohort1/Sample1')

    assert pipeline_instance.run.call_count == 1
    assert pipeline_instance.run.call_args[1] == {'samples': task.sample}

