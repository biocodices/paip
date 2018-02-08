import luigi
import json

from anotamela.recipes import annotate_vcf_rsids_with_clinvar

from paip.task_types import CohortTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateWithClinvar(CohortTask):
    """
    Takes a VCF and generates a .json file with annotations for all the
    rs IDs found.
    """
    OUTPUT = 'clinvar_variants.json'

    cache = luigi.Parameter(default='mysql')  # also: 'postgres', 'redis'
    http_proxy = luigi.Parameter(default='socks5://localhost:9050')

    # Receive an arbitrary JSON string with arguments for AnnotationPipeline.
    # They can be either annotation or cache keyword arguments.
    # If some argument is frequently used, you can extract it as a separate
    # parameter, as I already did with 'cache' and 'http_proxy' above.
    annotation_kwargs = luigi.Parameter(default='{}')

    def requires(self):
        # Remove the extra parameters that the annotation needs, but that
        # are not needed nor expected by the tasks upstream:
        params = self.param_kwargs.copy()

        del(params['cache'])
        del(params['http_proxy'])
        del(params['annotation_kwargs'])

        return FilterGenotypes(**params)

    def run(self):
        annotation_options = json.loads(self.annotation_kwargs)
        annotation_options.update({'cache': self.cache,
                                   'proxies': {'http': self.http_proxy}})

        annotate_vcf_rsids_with_clinvar(
            vcf_path=self.input().fn,
            output_json_path=self.output().fn,
            **annotation_options
        )
