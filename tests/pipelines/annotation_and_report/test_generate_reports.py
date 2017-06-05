from unittest.mock import mock_open, patch, Mock

import pytest

from paip.pipelines.annotation_and_report.generate_reports import GenerateReports
from paip.pipelines.annotation_and_report import TakeIGVSnapshots
import paip.pipelines.annotation_and_report.generate_reports


extra_params = {
    'templates_dir': '/path/to/templates',
    'translations_dir': '/path/to/translations',

    'min_reportable_category': 'CATEGORY',
    'min_odds_ratio': 1.5,
    'max_frequency': 0.5,
    'phenos_regex_list': '["pheno-1"]',
    'phenos_regex_file': '/path/to/phenos',
}


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(GenerateReports,
                               extra_params=extra_params)


def test_run(task, monkeypatch):
    # Mock the ReportsPipeline class so it returns a mocked instance:
    pipeline_instance = Mock()
    ReportsPipeline = Mock(return_value=pipeline_instance)
    monkeypatch.setattr(paip.pipelines.annotation_and_report.generate_reports,
                        'ReportsPipeline', ReportsPipeline)

    mock_TakeIGVSnapshots_instance = Mock(spec=TakeIGVSnapshots)
    mock_TakeIGVSnapshots = Mock(return_value=mock_TakeIGVSnapshots_instance)
    monkeypatch.setattr(paip.pipelines.annotation_and_report.generate_reports,
                        'TakeIGVSnapshots', mock_TakeIGVSnapshots)

    open_ = mock_open()
    with patch('paip.pipelines.annotation_and_report.generate_reports.open', open_):
        task.run()

    mock_TakeIGVSnapshots.assert_called_once()
    json_file = mock_TakeIGVSnapshots.call_args[1]['variants_json']
    assert json_file.endswith('variants.records.json')

    mock_TakeIGVSnapshots_instance.run.assert_called_once_with()

    # Check the reports generator has been called with the correct arguments

    assert ReportsPipeline.call_count == 1

    init_args = ReportsPipeline.call_args[1]

    for param_name, param_value in extra_params.items():
        if param_name == 'phenos_regex_list':
            assert init_args[param_name] == ['pheno-1']
            continue

        assert init_args[param_name] == param_value

    annotation_inputs = {
        'vep_tsv': 'vep.tsv',
        'genes_json': 'genes.json',
        'variants_json': 'rs_variants.json',
    }
    for name, filename in annotation_inputs.items():
        expected_file = pytest.helpers.file('Cohort1/Cohort1.{}'.format(filename))
        assert init_args[name] == expected_file

    assert init_args['genotypes_vcf'] == \
        pytest.helpers.file('Cohort1/Sample1/Sample1.reportable.eff.vcf')
    assert init_args['outdir'] == \
        pytest.helpers.file('Cohort1/Sample1')

    assert pipeline_instance.run.call_count == 1
    assert pipeline_instance.run.call_args[1] == {'samples': task.sample}

