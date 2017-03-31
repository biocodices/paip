import os
from os.path import join, dirname
import re
from itertools import chain, cycle
from operator import itemgetter
import json
from collections import OrderedDict

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from humanfriendly import format_number
import jinja2
from vcf_to_dataframe import vcf_to_dataframe

from paip.helpers import grouper, percentage


class CoverageAnalyser:
    """
    Generates coverage stats and plots given GATK DiagnoseTarget output.

    Usage:

        > cov_an = CoverageAnalyser(
              panel_vcf='path/to/..',
              coverage_files=['path/to/..', 'path/to/..']
          )
        > cov_an.report('Report Title', 'path/to/out.html')
          # => will create an HTML report with plots for all chromosomes.

    """

    COLOR_PALETTE = ('Vega10', 10)  # Name, number of colors to take
    MARKERS = 'xo*pshHP^v<>d'  # See matplotlib markers

    def __init__(self, panel_vcf, coverage_files, reads_threshold=30):
        """
        Pass the filepath to the Panel Variants VCF and a list of intervals
        stats files generated by GATK DiagnoseTargets tool.

        You can optionally specify where the coverage threshold will be
        drawn later in the plot with *reads_threshold*.
        """
        self.panel = self._read_panel(panel_vcf)
        self.intervals = self._read_coverage_files(coverage_files)
        self.reads_threshold = reads_threshold
        self._add_panel_data_to_intervals()
        self._generate_interval_names()

    def _read_panel(self, panel_vcf):
        """Read and parse the VCF with the panel variants."""
        panel = vcf_to_dataframe(panel_vcf)
        panel['chrom'] = panel['chrom'].astype(str)
        panel['genes'] = panel['info'].map(self._extract_genes).map(tuple)
        panel['varclass'] = panel['info'].map(lambda i: i.get('VC'))
        panel = panel.drop(['qual', 'filter', 'info', 'ref', 'alt'], axis=1)

        return panel

    def _read_coverage_files(self, coverage_files):
        """Read, parse and merge the VCFs of coverage per interval."""
        intervals = pd.DataFrame({})

        for fp in coverage_files:
            sample_intervals = vcf_to_dataframe(fp, keep_samples='all',
                                                keep_format_data=True)
            intervals = pd.concat([intervals, sample_intervals],
                                  ignore_index=True)

        intervals['LL'] = intervals['LL'].astype(int)
        intervals['ZL'] = intervals['ZL'].astype(int)
        intervals['IDP'] = intervals['IDP'].astype(float)
        intervals['end_pos'] = intervals['info'].map(itemgetter('END')).astype(int)
        intervals['length'] = intervals['end_pos'] - intervals['pos'] + 1
        # ^ + 1 because the end position is included

        return intervals

    def _add_panel_data_to_intervals(self):
        """Merge data from self.panel into self.intervals."""
        opts = dict(panel_variants=self.panel, axis=1, reduce=True)

        self.intervals['genes'] = \
            self.intervals.apply(self._find_genes, **opts).map(tuple)
        self.intervals['variants'] = \
            self.intervals.apply(self._find_variant_ids, **opts).map(tuple)
        self.intervals['variants_count'] = self.intervals['variants'].map(len)

    def _generate_interval_names(self):
        """Give each interval a unique ID and name for the plots."""

        def lines_of_n(variants, n):
            """List variants in groups of n per line."""
            in_groups = grouper(7, variants)
            return '\n'.join(', '.join(group) for group in in_groups)

        self.intervals['interval_name'] = (
            self.intervals['chrom'].astype(str) + ' : ' +
            self.intervals['pos'].astype(str).map(format_number) + ' – ' +
            self.intervals['end_pos'].astype(str).map(format_number) + ' | ' +
            self.intervals['genes'].str.join(', ') + '\n' +
            self.intervals['variants'].apply(lines_of_n, n=7)
        )

        interval_names = self.intervals['interval_name'].unique()
        interval_ids = dict(zip(interval_names, range(len(interval_names))))

        self.intervals['interval_id'] = \
            self.intervals['interval_name'].map(interval_ids)

    def _extract_genes(self, info):
        """
        Extract gene names from the INFO field of a dbSNP VCF.
        We're just keeping the gene names and return always a list.
        Example: PINK1-AS:100861548|PINK1:65018 => ['PINK1-AS', 'PINK'].
        """
        genes_value = info.get('GENEINFO', '')
        genes = [gene.split(':')[0] for gene in genes_value.split('|')]
        return [gene for gene in genes if gene]

    _find_variants_cache = {}
    def _find_variants(self, interval, panel_variants):
        """
        Given an interval with 'pos' and 'end_pos', finds the *panel_variants*
        that are contained in it. Returns a list of variants (as DataFrame).
        """
        # Check chrom comparison will be string vs. string!
        assert isinstance(interval['chrom'], str)
        assert isinstance(panel_variants['chrom'].iloc[0], str)

        key = '{0.chrom}:{0.pos}:{0.end_pos}'.format(interval)

        if key not in self._find_variants_cache:
            same_chrom = panel_variants['chrom'] == interval['chrom']
            start_after = panel_variants['pos'] >= interval['pos']
            end_before = panel_variants['pos'] <= interval['end_pos']
            contained_variants = panel_variants[same_chrom & start_after & end_before]
            self._find_variants_cache[key] = contained_variants

        return self._find_variants_cache[key]

    def _find_variant_ids(self, interval, panel_variants):
        """
        Given an interval with 'pos' and 'end_pos', finds the *panel_variants*
        that are contained in it and returns a list of their IDs.
        """
        contained_variants = self._find_variants(interval, panel_variants)
        return list(contained_variants['id'])

    def _find_genes(self, interval, panel_variants):
        """
        Given an interval with 'pos' and 'end_pos', finds the *panel_variants*
        that are contained in it and returns a list of the genes they're in.
        """
        contained_variants = self._find_variants(interval, panel_variants)
        return sorted(set(chain.from_iterable(contained_variants['genes'])))

    def plot(self, basename):
        """
        Plots the coverage per sample, interval and chromosome.
        Saves the figures (one per chromosome) using *basename* path as a
        base for the filepath, adding a 'chrom_N.png' suffix each time.
        """
        self._define_sample_colors_and_markers()
        self.plot_files = []

        sns.set_style('darkgrid')

        for chrom, chrom_intervals in self.intervals.groupby('chrom'):
            intervals_here = chrom_intervals['interval_id'].unique()

            # Define plot size
            fig_height = 2 + len(intervals_here) / 2
            fig_width = 10
            tall_fig = fig_height > 7

            # Create the figure and plot the datapoints
            fig = plt.figure(figsize=(fig_width, fig_height))
            ax = fig.add_subplot(1, 1, 1)

            # One series for each sample to use different markers and colors
            by_sample = chrom_intervals.groupby('sample_id')

            for sample, chrom_sample_intervals in by_sample:

                chrom_sample_intervals.plot.scatter(
                    ax=ax, x='IDP', y='interval_id',
                    c=self.sample_colors[sample],
                    marker=self.sample_markers[sample],
                    label=sample,
                    s=40, alpha=0.8,
                )

            # Plot the mean depth at each interval
            by_interval = chrom_intervals.groupby('interval_id')

            mean_label_added = False
            for interval_id, interval_coverage in by_interval:
                mean = interval_coverage['IDP'].mean()
                opts = dict(x=mean, y=interval_id, c='Lime', s=350, marker='|',
                            zorder=0)

                if not mean_label_added:
                    opts.update({'label': 'Samples\nmean'})
                    mean_label_added = True

                ax.scatter(**opts)

            # Plot aesthetics
            ax.set_title('Coverage in Chromosome {}'.format(chrom),
                         y=1.06, fontdict={'size': 17})
            ax.set_ylabel('Interval')
            ax.set_xlabel('Read Depth (hiding datapoints > 500X)')
            ax.set_yticks(intervals_here)
            ax.set_yticklabels(chrom_intervals['interval_name'].unique())
            ax.axvline(30, color='FireBrick', linestyle='dashed', linewidth=1)
            ax.grid(axis='y', color='white')
            ax.set_ylim([min(intervals_here) - 1, max(intervals_here) + 1])

            # Make all x axis the same to ease the comparison between plots
            ax.set_xticks(sorted([0, 100, 200, 300, 400, 500,
                                  self.reads_threshold]))
            ax.set_xlim([-5, max(self.reads_threshold + 100, 500)])

            if tall_fig:
                ax.tick_params(top='on', labeltop='on')
            ax.tick_params(axis='both', direction='out', length=5,
                           color='#888888')

            # Legend aesthetics
            ax.legend(
                title='Samples', frameon=True, facecolor='white',
                ncol=1 if tall_fig else 7,
                bbox_to_anchor=(1, 1) if tall_fig else (0.5, -0.25),
                loc='upper left' if tall_fig else 'upper center',
            )

            # Separation lines between genes
            genes_here = chrom_intervals.set_index('interval_id')['genes']
            for i, gene in enumerate(genes_here.unique()):
                if gene == ('',) or i == 0:
                    continue

                y_value = min(genes_here[genes_here == gene].index)
                ax.axhline(y=y_value - 0.5, linewidth=1,
                           linestyle='solid', color='#BBBBBB')

            filepath = basename + '_chrom_{}.png'.format(chrom)
            plt.savefig(filepath, bbox_inches='tight', dpi=150)
            self.plot_files.append(filepath)
            plt.close()

        return self.plot_files

    def _define_sample_colors_and_markers(self):
        """Define a unique color & marker for each sample."""
        samples = self.intervals['sample_id'].unique()
        colors = cycle(sns.color_palette(*self.COLOR_PALETTE))
        markers = cycle(self.MARKERS)
        self.sample_colors = dict(zip(samples, colors))
        self.sample_markers = dict(zip(samples, markers))

    def make_html_report(self, report_title, plot_files, destination_path):
        """
        Puts the *plot_files* in an HTML report and saves it at
        *destination_path*. The *report_title* will be used as the document
        heading.
        """
        plot_paths = sorted(plot_files, key=self._plot_file_chrom_index)

        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('paip', 'templates'),
            autoescape=jinja2.select_autoescape(['html'])
        )

        template = jinja_env.get_template('coverage_report.html.jinja')
        template_data = {'plot_paths': plot_paths,
                         'report_title': report_title}
        html = template.render(template_data)

        with open(destination_path, 'w') as f:
            f.write(html)

        return destination_path

    def _plot_file_chrom_index(self, filename):
        """
        Find the chromosome name in a plot filename and return the chromosome
        index to aid the sorting.
        """
        chrom = re.search(r'_chrom_(.+)\.png', filename).group(1)
        order = [str(n) for n in range(1, 23)] + ['X', 'Y', 'MT']
        return order.index(chrom)

    def report(self, report_title, destination_path):
        """
        Makes an HTML report with plots in *destination_path*. Returns the
        filepath to the report. Will put the plots in a subdirectory named
        "coverage_plots".
        """
        if not destination_path.endswith('.html'):
            destination_path += '.html'

        plots_dir = join(dirname(destination_path), 'coverage_plots')
        os.makedirs(plots_dir, exist_ok=True)
        plots_basename = join(plots_dir, 'coverage')

        plot_files = self.plot(plots_basename)
        html_file = self.make_html_report(report_title, plot_files,
                                          destination_path)

        return html_file

    def summarize_coverage(self):
        """
        Given a dataframe of a *single sample* in self.intervals,
        generates a summary of the coverage data as a dict. All rows
        should belong to the same sample for this to make sense.

        This will work if only ONE DiagnoseTargets VCF has been fed
        to the CoverageAnalyser (that is, from only one sample).

        This data is later used by MultiQC.
        """
        assert len(self.intervals['sample_id'].unique()) == 1

        data = {}

        total_bases = self.intervals['length'].sum()
        idp_by_length = self.intervals['IDP'] * self.intervals['length']
        data['mean_DP'] = round(idp_by_length.sum() / total_bases, 2)
        data['std_DP'] = round(idp_by_length.std() / total_bases, 2)

        data['% bases with LOW DP'] = percentage(self.intervals['LL'].sum(),
                                                 total_bases,
                                                 decimal_places=2)

        data['% bases with NO READS'] = percentage(self.intervals['ZL'].sum(),
                                                   total_bases,
                                                   decimal_places=2)

        # Filter counts:
        # NOTE: We need to convert numbers to int because numpy types
        # aren't serializable.
        data.update({'{} intervals'.format(k.replace(';', ' & ')): int(v)
                    for k, v in self.intervals['FT'].value_counts().items()})

        return data

    def json_coverage_summary_for_multiqc(self, sample_id, module_name):
        """
        Return the coverage summary JSON-formatted for MultiQC. Specify a
        *module_name* for MultiQC to identify this data.
        """
        data = self.summarize_coverage()
        sorted_data = OrderedDict(sorted(data.items()))
        multiqc_data = {'id': module_name,
                        'data': {sample_id: sorted_data}}
        return json.dumps(multiqc_data, sort_keys=True, indent=4)

