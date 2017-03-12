from collections import OrderedDict

import paip
from paip.pipelines.variant_calling import *
from paip.pipelines.quality_control import *
from paip.pipelines.variant_calling_task import VariantCalling
from paip.pipelines.quality_control_task import QualityControl
from paip.pipelines.annotate_variants import AnnotateVariants


def list_tasks():
    """List all pipeline tasks available."""
    return OrderedDict([
        ('Variant Calling tasks',
         list(paip.pipelines.variant_calling.__dict__.items())),

        ('Quality Control tasks',
         list(paip.pipelines.quality_control.__dict__.items())),

        ('Other tasks',
         list(paip.pipelines.__dict__.items())),
    ])

