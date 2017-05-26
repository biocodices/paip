from os.path import basename

from paip.helpers import path_to_resource
from paip.task_types import CohortTask


class VizCNVs(CohortTask):
    """
    Take the result of the CNV Calling pipeline and run the R scripts provided
    by the XHMM software to produce several visualizations.
    """
    SUBDIR = 'xhmm_run'

    def run(self):
        self.copy_R_script()
        self.edit_R_script_variables()

    # Create the plots directory before executing the R script

    # Add Rscript to executables

    # Run Rscript make_XHMM_plots.R

    def copy_and_edit_R_script(self):
        """
        Copy the example R script from the XHMM directory to the Cohort's
        xhmm run directory and edit its definitions of PLOT_PATH, JOB_PREFICES,
        and JOB_TARGETS_TO_GENES.
        """
        xhmm_R_script = path_to_resource('xhmm_R_script')

        with open(xhmm_R_script) as f:
            script_lines = [line for line in f]

        variables_to_change = {
            'PLOT_PATH': self.path('plots', prefix=False),
            'JOB_PREFICES': self.path('DATA'),
            'JOB_TARGETS_TO_GENES': path_to_resource('panel_annotated_intervals'),
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
                                  .replace('example_', ''))

        with open(edited_script, 'w') as f:
            for line in edited_script_lines:
                f.write(line)

