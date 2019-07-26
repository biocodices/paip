import json
import luigi

from paip.task_types import CohortTask


class CohortAnnotationTask(CohortTask):
    """
    Base luigi task to use anotala's annotation services.
    Deals with extra parameters like proxies and cache.
    """
    cache = luigi.Parameter(default='mysql')  # also: 'postgres', 'redis'
    http_proxy = luigi.Parameter(default='socks5://localhost:9050')

    # Receive an arbitrary JSON string with more arguments for AnnotationPipeline.
    # If some argument is frequently used, you can extract it as a separate
    # parameter, as I already did with 'cache' and 'http_proxy' above.
    extra_annotation_kwargs = luigi.Parameter(default='{}')

    def requires(self):
        # Save the annotation parameters in an instance variable:
        annotation_keys = ['cache', 'http_proxy', 'extra_annotation_kwargs']
        annotation_params = {key: self.param_kwargs[key]
                             for key in annotation_keys}

        # And remove these parameters temporarily from self.param_kwargs,
        # because this dictionary will be used to initialize the tasks upstream,
        # and they are NOT expecting annotation arguments:
        for key in annotation_keys:
            del(self.param_kwargs[key])

        # The rest of the processing, i.e. assigning the cohort parameters of
        # this task to the tasks upstream, is done by CohortTask in the
        # super() call:
        required_tasks = super().requires()

        # Finally, restore the annotation parameters to param_kwargs so that
        # they are correctly displayed by luigi logging
        for key in annotation_keys:
            self.param_kwargs[key] = annotation_params[key]

        # And do some parsing of the annotation parameters, to facilitate
        # their use by anotala's library. This parsed version is stored
        # in self.annotation_kwargs:
        self.annotation_kwargs = \
            json.loads(annotation_params['extra_annotation_kwargs'])
        self.annotation_kwargs.update({
            'cache': annotation_params['cache'],
            'proxies': {'http': annotation_params['http_proxy']}
        })

        return required_tasks
