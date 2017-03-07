from collections import OrderedDict
import json

from vcf_to_dataframe import vcf_to_dataframe


class PanelMetricsGenerator:
    """
    Generates some metrics about the panel variants and the seen genotypes in
    a single-sample VCF. Usage:

        > pmg = PanelMetricsGenerator('sampleX.vcf', 'sampleX', 'panel.vcf')
        > pmg.compute_metrics()
        > pmg.metrics  # => dict with computed metrics

    """

    def __init__(self, sample_vcf, sample_name, panel_vcf, min_gq, min_dp):
        """
        Pass a VCF with the sample genotypes and a VCF of the Panel variants.
        Metrics will be stored in self.metrics.
        """
        self.sample = sample_name
        self.min_gq = min_gq
        self.min_dp = min_dp
        self.panel = vcf_to_dataframe(panel_vcf)
        self.panel_ids = list(self.panel['id'])
        self.panel_size = len(self.panel_ids)
        self.genos = vcf_to_dataframe(sample_vcf, keep_samples=sample_name,
                                      keep_format_data=True)
        self.genos['in_panel'] = self.genos['id'].apply(self.belongs_to_panel)
        self.panel_genos = self.genos[self.genos['in_panel']]
        self.metrics = {}

    def compute_metrics(self):
        """
        Wrapper method to compute all metrics and store them in self.metrics.
        """
        self.count_total_genos()
        self.count_seen_variants()
        self.count_missing_variants()
        self.count_genotypes()
        self.count_badqual_genotypes()
        self.compute_GQ_DP_stats()

        return self.metrics

    def json_metrics_for_multiqc(self, module_name):
        """
        Return the metrics JSON-formatted for MultiQC. Specify a *module_name*
        for MultiQC to identify this data. Tries to compute metrics if no
        data has been generated yet.
        """
        if not self.metrics:
            self.compute_metrics()

        sorted_metrics = OrderedDict(sorted(self.metrics.items()))

        metrics = {'id': module_name, 'data': {self.sample: sorted_metrics}}
        return json.dumps(metrics, sort_keys=True, indent=4)

    def count_total_genos(self):
        self.metrics['Total genos'] = len(self.genos['id'])

    def count_seen_variants(self):
        """Count variants/genotypes in and out of the panel."""
        counts = self.genos['in_panel'].value_counts().to_dict()
        # (We need to convert to int because numpy numbers aren't serializable)
        self.metrics['Panel genos'] = seen_n = int(counts.get(True) or 0)
        self.metrics['Extra-panel genos'] = int(counts.get(False) or 0)
        self.metrics['% Panel seen'] = self.percentage(seen_n, self.panel_size)

    def count_missing_variants(self):
        """Count panel variants that are not seen in the sample VCF."""
        seen_ids = ' '.join(self.genos['id'])
        missing_variants = [rsid for rsid in self.panel_ids
                            if rsid not in seen_ids]
        self.metrics['Panel variants missing'] = len(missing_variants)
        self.metrics['% Panel missing'] = self.percentage(len(missing_variants),
                                                          self.panel_size)

    def count_genotypes(self):
        """Counts per seen genotype type among the panel variants."""
        counts = self.panel_genos['GT'].value_counts().to_dict()

        # (We need to convert to int because numpy numbers aren't serializable)
        self.metrics['Panel 0/0'] = int((counts.get('0/0') or 0) +
                                        (counts.get('0|0') or 0) +
                                        (counts.get('0') or 0))

        self.metrics['Panel 0/1'] = int((counts.get('0/1') or 0) +
                                        (counts.get('0|1') or 0))

        self.metrics['Panel 1/1'] = int((counts.get('1/1') or 0) +
                                        (counts.get('1|1') or 0) +
                                        (counts.get('1') or 0))

        self.metrics['Panel ./.'] = int((counts.get('./.') or 0) +
                                        (counts.get('.') or 0))

    def count_badqual_genotypes(self):
        """Counts genotypes with low GQ and/or low DP."""
        in_panel = self.genos['in_panel']

        low_dp = self.genos['DP'] < self.min_dp
        self.metrics['Panel LowDP'] = len(self.genos[in_panel & low_dp])

        low_gq = self.genos['GQ'] < self.min_gq
        self.metrics['Panel LowGQ'] = len(self.genos[in_panel & low_gq])

        nopass = self.genos['filter'] != 'PASS'
        self.metrics['Panel non-PASS'] = len(self.genos[in_panel & nopass])

        missing_geno = self.genos['GT'].isin(['.', './.'])

        bad_q = (low_dp | low_gq | nopass | missing_geno)
        self.metrics['Panel non-reportable'] = bq = len(self.genos[in_panel & bad_q])

        panel_size = len(self.genos[in_panel])
        self.metrics['Panel non-reportable %'] = self.percentage(bq, panel_size)

    def compute_GQ_DP_stats(self):
        """Compute some stats on GQ and DP."""
        self.metrics['DP mean'] = int(self.panel_genos['DP'].mean())
        self.metrics['GQ mean'] = int(self.panel_genos['GQ'].mean())

    def belongs_to_panel(self, rsid):
        """Check if an rs ID belongs to the panel."""
        rsids = rsid.split(';') if ';' in rsid else [rsid]
        # ^ Deal with multiple concatenated IDs in the VCF, like "rs123;rs234"

        for rsid in rsids:
            if rsid in self.panel_ids:
                return True

        return False

    @staticmethod
    def percentage(n, total):
        if total == 0:
            return 0

        return round(100 * n / total)

