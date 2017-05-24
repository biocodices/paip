from paip.task_types import CohortTask


class VizCNVs(CohortTask):
    """
    Take the result of the CNV Calling pipeline and run the R scripts provided
    by the XHMM software to produce several visualizations.
    """

    # Add the path to example_make_XHMM_plots.R to resources

    # Copy the R script example_make_XHMM_plots.R from the software dir
    # to the xhmm_run dir.

    # Edit the variables in the copied version of the script:
    # XHMM_PATH, PLOT_PATH, JOB_PREFICES, JOB_TARGETS_TO_GENES

    # Add Rscript to executables

    # Run Rscript make_XHMM_plots.R

