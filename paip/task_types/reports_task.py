import luigi


class ReportsTask:
    """
    Abstract class to provide common parameters to GenerateReports and
    GenerateReportsCohort. See the former class for a full explanation of
    each parameter.
    """
    # Reportable variants settings
    min_odds_ratio = luigi.FloatParameter(default=1)  # All by default
    max_frequency = luigi.FloatParameter(default=1)  # All by default
    min_reportable_category = luigi.Parameter(default='DRUG')
    phenos_regex_list = luigi.Parameter(default=None)
    phenos_regex_file = luigi.Parameter(default=None)

    EXTRA_PARAMS = [
        'min_odds_ratio',
        'max_frequency',
        'min_reportable_category',
        'phenos_regex_list',
        'phenos_regex_file',
    ]

    def sample_params(self):
        """
        Remove the extra parameters that the report generation needs, but
        that are not needed or expected by the tasks upstream:
        """
        sample_params = self.param_kwargs.copy()

        for param_name in self.EXTRA_PARAMS:
            del(sample_params[param_name])

        return sample_params


    def cohort_params(self):
        """
        Remove all the extra parameters of the report generation and also
        remove the 'sample' parameter of the SampleTask.
        """
        cohort_params = self.sample_params()
        del(cohort_params['sample'])
        return cohort_params
