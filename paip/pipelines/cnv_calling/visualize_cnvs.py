import os
from os.path import basename

import luigi

from paip.pipelines.cnv_calling import DiscoverCNVs
from paip.task_types import CohortTask


class VisualizeCNVs(CohortTask):
    """
    Take the result of the CNV Calling pipeline and run the R scripts provided
    by XHMM to produce several visualizations.
    """
    SUBDIR = 'xhmm_run'
    REQUIRES = DiscoverCNVs

    @property
    def plot_path(self):
        return self.path('plots', prefix=False)

    def run(self):
        self.copy_and_edit_R_script()
        os.makedirs(self.plot_path, exist_ok=True)

        program_name = 'Rscript make_XHMM_plots'
        program_options = {
            'script_path': self.path('make_XHMM_plots.R', prefix=False)
        }
        self.run_program(program_name, program_options)

    def output(self):
        return luigi.LocalTarget(self.plot_path)

    def copy_and_edit_R_script(self):
        """
        Copy the example R script from the resources directory to the Cohort's
        xhmm run subdirectory and edit its definitions of PLOT_PATH,
        JOB_PREFICES, and JOB_TARGETS_TO_GENES.
        """
        xhmm_R_script = self.config.resources['xhmm_R_script']

        with open(xhmm_R_script) as f:
            script_lines = [line for line in f]

        variables_to_change = {
            'PLOT_PATH': self.plot_path,
            'JOB_PREFICES': self.path('DATA'),
            'JOB_TARGETS_TO_GENES': self.config.resources['panel_annotated_intervals'],
        }

        edited_script_lines = []

        for script_line in script_lines:

            for variable_name, new_value in variables_to_change.items():
                if script_line.startswith(variable_name + ' = '):
                    script_line = '{} = "{}"\n'.format(variable_name,
                                                       new_value)
                    break

            edited_script_lines.append(script_line)

        edited_script = self.path(basename(xhmm_R_script)
                                  .replace('example_', ''), prefix=False)

        with open(edited_script, 'w') as f:
            for line in edited_script_lines:
                f.write(line)

