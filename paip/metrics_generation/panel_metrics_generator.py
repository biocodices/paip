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

    def __init__(self, sample_vcf, sample_name, panel_vcf):
        """
        Pass a VCF with the sample genotypes and a VCF of the Panel variants.
        Metrics will be stored in self.metrics.
        """
        self.sample = sample_name
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
        self.metrics['total_genos'] = len(self.genos['id'])

    def count_seen_variants(self):
        """Count variants/genotypes in and out of the panel."""
        counts = self.genos['in_panel'].value_counts().to_dict()
        # (We need to convert to int because numpy numbers aren't serializable)
        self.metrics['panel_genotypes_seen'] = seen_n = int(counts.get(True) or 0)
        self.metrics['extra_panel_genotypes_seen'] = int(counts.get(False) or 0)

        self.metrics['panel_genotypes_seen_%'] = self.percentage(seen_n,
                                                                 self.panel_size)

    def count_missing_variants(self):
        """Count panel variants that are not seen in the sample VCF."""
        seen_ids = ' '.join(self.genos['id'])
        missing_variants = [rsid for rsid in self.panel_ids
                            if rsid not in seen_ids]
        self.metrics['panel_genotypes_missing'] = len(missing_variants)
        self.metrics['panel_missing_%'] = self.percentage(len(missing_variants),
                                                          self.panel_size)

    def count_genotypes(self):
        """Counts per seen genotype type among the panel variants."""
        total = len(self.panel_genos)
        counts = self.panel_genos['GT'].value_counts().to_dict()

        # FIXME: This doesn't take into account the hemicygotes and the 0|0

        # (We need to convert to int because numpy numbers aren't serializable)
        self.metrics['panel_homRef_count'] = homref = int(counts.get('0/0') or 0)
        self.metrics['panel_het_count'] = het = int(counts.get('0/1') or 0)
        self.metrics['panel_homAlt_count'] = homalt = int(counts.get('1/1') or 0)

        self.metrics['panel_homRef_%'] = self.percentage(homref, total)
        self.metrics['panel_het_%'] = self.percentage(het, total)
        self.metrics['panel_homAlt_%'] = self.percentage(homalt, total)

    def compute_GQ_DP_stats(self):
        """Compute some stats on GQ and DP."""
        self.metrics['DP_mean'] = int(self.panel_genos['DP'].mean())
        self.metrics['GQ_mean'] = int(self.panel_genos['GQ'].mean())

        self.metrics['DP_median'] = int(self.panel_genos['DP'].median())
        self.metrics['GQ_median'] = int(self.panel_genos['GQ'].median())

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

