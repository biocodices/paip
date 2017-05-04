import os
from os.path import join, dirname
import re
from itertools import chain, cycle
from operator import itemgetter
import json
from math import sqrt
from collections import OrderedDict

import numpy as np
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

    Usage to generate an HTML report with all the plots:

        > cov_an = CoverageAnalyser(
              panel_vcf='path/to/..',
              coverage_files=['path/to/..', 'path/to/..']
          )
        > cov_an.report('Report Title', 'path/to/out.html')
          # => will create an HTML report with plots for all chromosomes.

    Usage for Jupyter:

        > ca = CoverageAnalyser(coverage_files=[...])
        > ca.plot_boxplot()
        > ca.plot_coverage_per_chromosome()
        > ca.plot_heatmap()

    """

    COLOR_PALETTE = ('Vega10', 10)  # Name, number of colors to take
    MARKERS = 'xo*pshHP^v<>d'

    def __init__(self, coverage_files, panel_vcf=None, reads_threshold=30):
        """
        Pass list of intervals stats files generated by GATK DiagnoseTargets
        tool. Optionally, pass the filepath to the Panel Variants VCF so
        specific regions/variants can be plotted.

        You can optionally specify where the coverage threshold will be
        drawn later in the plot with *reads_threshold*.
        """
        self.intervals = self._read_coverage_files(coverage_files)
        self.reads_threshold = reads_threshold

        self.has_panel = panel_vcf is not None

        if self.has_panel:
            self.panel = self._read_panel(panel_vcf)
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
        """
        Give each interval a unique ID, name, and short name for the plots.
        """

        def lines_of_n(variants, n):
            """List variants in groups of n per line."""
            in_groups = grouper(7, variants)
            return '\n'.join(', '.join(group) for group in in_groups)

        self.intervals['interval_name'] = (
            self.intervals['chrom'].astype(str) + ' : ' +
            self.intervals['pos'].astype(str).map(format_number) + ' – ' +
            self.intervals['end_pos'].astype(str).map(format_number)
        )

        if self.has_panel:
            # If there's a panel of variants, we have extra info to add
            # to the interval names.
            self.intervals['interval_name'] = (
                self.intervals['interval_name'] + ' | ' +
                self.intervals['genes'].str.join(', ') + '\n' +
                self.intervals['variants'].apply(lines_of_n, n=7)
            )

        interval_names = self.intervals['interval_name'].unique()
        interval_ids = dict(zip(interval_names, range(len(interval_names))))

        self.intervals['interval_id'] = \
            self.intervals['interval_name'].map(interval_ids)

        padded_indices = (self.intervals['interval_id'] + 1).map(
            lambda ix: '{:04}'.format(ix)
        )
        self.intervals['interval_short_name'] = (
            '[' + padded_indices + '] ' +
            self.intervals['chrom'].astype(str) + ': ' +
            self.intervals['pos'].astype(str).map(format_number) + '–' +
            self.intervals['end_pos'].astype(str).map(format_number)
        )

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

    def _make_coverage_matrix(self):
        """
        Return a coverage matrix of samples vs. intervals with the data from
        self.intervals.
        """
        return self.intervals.pivot(index='sample_id',
                                    columns='interval_short_name',
                                    values='IDP')

    def plot_heatmap(self, max_value, colormap='Reds_r', dest_dir=None, **kwargs):
        """
        Use self.intervals coverage data to plot a heatmap of samples vs.
        regions read depth. If *dest_dir* is provided, saves the figure at
        *dest_dir*/coverage_heatmap.png; else, it returns the axes.

        *max_value* is the threshold over which the top color of the colormap
        is used. The heatmap is meant to highlight low coverage targets, so
        *max_value* should be the pipeline depth threshold. This means all
        targets that pass the threshold will be plotted with the same color,
        and the low coverage ones will be highlighted against that background).

        Optionally, select a different *colormap* from matplolib available
        colormaps.

        Extra *kwargs* will be passed to seaborn.heatmap().
        """
        coverage_matrix = self._make_coverage_matrix()

        sns.set(style='ticks', context='notebook')

        fig = plt.figure(figsize=(25, 4))
        ax = fig.add_subplot(1, 1, 1)
        ax = sns.heatmap(coverage_matrix, ax=ax,
                         cbar_kws={'pad': 0.045, 'label': 'Read Depth'},
                         vmin=0, vmax=max_value, cmap=colormap, **kwargs)
        ax.set_xlabel('Interval')
        ax.set_ylabel('Sample')
        ax.set_title('Low Coverage Targets (Read Depth < {})'
                     .format(max_value), y=1.08, fontsize=13)

        # Keep the target labels where at least 10% of the samples have less
        # than *max_value* read depth:
        Q10_per_interval = coverage_matrix.quantile(0.10)
        subthreshold = Q10_per_interval < max_value
        problematic_intervals = Q10_per_interval[subthreshold].index

        xticks = ax.get_xticks()
        xlabels = [lab.get_text() for lab in ax.get_xticklabels()]
        xticks_labels = {label: xval for xval, label in zip(xticks, xlabels)
                         if label in problematic_intervals}

        ax.set_xticks(list(xticks_labels.values()))
        ax.set_xticklabels(list(xticks_labels.keys()), rotation='vertical',
                           fontsize=7)

        ax.tick_params(axis='y', right='on', labelright='on')
        ax.set_yticklabels(ax.get_yticklabels(), rotation='horizontal')

        ax.hlines(ax.get_yticks() + 0.5, *ax.get_xlim(), color='Silver',
                  linewidth=0.5)

        if dest_dir:
            filepath = os.path.join(dest_dir, 'coverage_heatmap.png')
            plt.savefig(filepath, bbox_inches='tight', dpi=150)
            plt.close()

            self.heatmap_plot = filepath

            return filepath

        return ax

    def plot_boxplot(self, dest_dir=None):
        """
        Uses the read depths in self.intervals to make a boxplot of coverage
        per sample.

        If *dest_dir* is provided, the figure will be saved in that directory.
        Else, the matplotlib axes instance will be returned.
        """
        sns.set(style='ticks', context='paper', font_scale=1)

        fig = plt.figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)

        medians = self.intervals.groupby('sample_id')['IDP'].median()
        sample_order = medians.sort_values().index

        sns.boxplot(
            ax=ax, data=self.intervals, x='sample_id', y='IDP',
            order=sample_order, color='Gray',

            # Tufte style options:
            showcaps=False, showbox=False,
            width=0.1, linewidth=1,
            medianprops={'linestyle': '-', 'color': 'DodgerBlue',
                         'linewidth': 4},
            flierprops={'markerfacecolor': 'DarkGray', 'marker': '.',
                        'markersize': 3}
        )

        samples = self.intervals['sample_id'].unique()
        ax.set_xticklabels(ax.get_xticklabels(),
                           rotation=45 if len(samples) > 10 else 0)

        ax.tick_params(axis='both', color='Silver')
        ax.set_ylim([-10, self.intervals['IDP'].max()])
        ax.set_xlabel('Sample', labelpad=20)
        ax.set_ylabel('Read Depth', labelpad=20)

        # We want to discriminate the low values in a more granular way, so:
        ax.set_yticks([100, 200, 300, 400], minor=True)

        # Draw the global median
        sequencing_median = self.intervals['IDP'].median()
        seq_median_pretty = format_number(sequencing_median, num_decimals=0)
        ax.axhline(y=sequencing_median, color='DodgerBlue', linewidth=1,
                   linestyle='dotted')
        ax.text(x=max(ax.get_xticks()) + 0.6, color='DodgerBlue',
                y=sequencing_median, s='$median={}$'.format(seq_median_pretty),
                verticalalignment='center', horizontalalignment='left')

        ax.set_title('Coverage per Sample', y=1.08)

        sns.despine()
        ax.spines['left'].set_color('Silver')
        ax.spines['bottom'].set_color('Silver')

        if dest_dir:
            filepath = os.path.join(dest_dir, 'coverage_boxplot.png')
            plt.savefig(filepath, bbox_inches='tight', dpi=150)
            plt.close()
            return filepath

        return ax

    def plot_coverage_per_chromosome(self, basename=None, plt_show=True):
        """
        Plots the coverage per sample, interval and chromosome.

        If *basename* is provided, saves the figures (one per chromosome) using
        *basename* path as a base for the filepath, adding a 'chrom_N.png'
        suffix each time.

        If no *basename* is passed, it returns the matplotlib axes.
        """
        self._define_sample_colors_and_markers()

        plot_files = []
        axes_list = []

        sns.set(style='darkgrid')

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
                         y=1.06, fontdict={'size': 12})
            ax.set_ylabel('Interval')
            ax.set_xlabel('Read Depth (hiding datapoints > 500X)')
            ax.set_yticks(intervals_here)
            ax.set_yticklabels(chrom_intervals['interval_name'].unique())
            ax.axvline(self.reads_threshold, color='FireBrick',
                       linestyle='dashed', linewidth=1)
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
            if 'genes' in chrom_intervals:
                genes_here = chrom_intervals.set_index('interval_id')['genes']
                for i, gene in enumerate(genes_here.unique()):
                    if gene == ('',) or i == 0:
                        continue

                    y_value = min(genes_here[genes_here == gene].index)
                    ax.axhline(y=y_value - 0.5, linewidth=1,
                            linestyle='solid', color='#BBBBBB')

            if basename:
                filepath = basename + '_chrom_{}.png'.format(chrom)
                plt.savefig(filepath, bbox_inches='tight', dpi=150)
                plot_files.append(filepath)
                plt.close()
            else:
                axes_list.append(ax)
                if plt_show:
                    plt.show()

        return plot_files or axes_list  # One of these will be empty

    def _define_sample_colors_and_markers(self):
        """Define a unique color & marker for each sample."""
        samples = self.intervals['sample_id'].unique()
        colors = cycle(sns.color_palette(*self.COLOR_PALETTE))
        markers = cycle(self.MARKERS)
        self.sample_colors = dict(zip(samples, colors))
        self.sample_markers = dict(zip(samples, markers))

    def _plot_file_chrom_index(self, filename):
        """
        Find the chromosome name in a plot filename and return the chromosome
        index to aid the sorting.
        """
        chrom = re.search(r'_chrom_(.+)\.png', filename).group(1)
        order = [str(n) for n in range(1, 23)] + ['X', 'Y', 'MT']
        return order.index(chrom)

    def make_html_report(self, report_title, boxplot_path, heatmap_path,
                         chrom_plot_paths, destination_path):
        """
        Puts the plots from *heatmap_path*, *boxplot_path* and
        *chrom_plot_paths* in an HTML report and saves it at
        *destination_path*. The *report_title* will be used as the document
        heading.
        """
        chrom_plot_paths = sorted(chrom_plot_paths,
                                  key=self._plot_file_chrom_index)

        jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('paip', 'templates'),
            autoescape=jinja2.select_autoescape(['html'])
        )

        template = jinja_env.get_template('coverage_report.html.jinja')
        template_data = {'boxplot_path': boxplot_path,
                         'heatmap_path': heatmap_path,
                         'chrom_plot_paths': chrom_plot_paths,
                         'report_title': report_title}
        html = template.render(template_data)

        with open(destination_path, 'w') as f:
            f.write(html)

        return destination_path

    def report(self, report_title, destination_path):
        """
        Makes an HTML report with plots in *destination_path*. Returns the
        filepath to the report. Will put the plots in a subdirectory named
        "coverage_plots".
        """
        # Make the plots, get their filepaths
        plots_dir = join(dirname(destination_path), 'coverage_plots')
        os.makedirs(plots_dir, exist_ok=True)
        boxplot_path = self.plot_boxplot(dest_dir=plots_dir)
        heatmap_path = self.plot_heatmap(dest_dir=plots_dir,
                                         max_value=self.reads_threshold)
        chrom_plots_basename = join(plots_dir, 'coverage')
        chrom_plot_paths = self.plot_coverage_per_chromosome(chrom_plots_basename)

        # Put the plots in the HTML
        if not destination_path.endswith('.html'):
            destination_path += '.html'

        html_file = self.make_html_report(
            report_title,
            boxplot_path,
            heatmap_path,
            chrom_plot_paths,
            destination_path
        )

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
        std = self._weighted_std(self.intervals['IDP'],
                                 weights=self.intervals['length'])
        data['std_DP'] = round(std, 2)

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

    @staticmethod
    def _weighted_std(values, weights):
        """
        Return the weighted standard deviation.

        values, weights -- Numpy ndarrays with the same shape.

        Taken from http://stackoverflow.com/questions/2413522
        """
        average = np.average(values, weights=weights)
        variance = np.average((values - average)**2, weights=weights)
        return sqrt(variance)

