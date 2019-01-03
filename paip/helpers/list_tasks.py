from collections import OrderedDict

import luigi

import paip
from paip.pipelines.variant_calling import *
from paip.pipelines.ion_torrent import *
from paip.pipelines.quality_control import *
from paip.pipelines.annotation_and_report import *
from paip.pipelines.cnv_calling import *
from paip.pipelines.variant_calling_task import VariantCalling
from paip.pipelines.cnv_calling_task import CNVCalling
from paip.pipelines.quality_control_task import QualityControl


def list_tasks():
    """List all pipeline tasks available."""
    wrapper_tasks = {'VariantCalling': VariantCalling,
                     'QualityControl': QualityControl,
                     'CNVCalling': CNVCalling}

    objects = OrderedDict([
        ('Wrapper Tasks', list(wrapper_tasks.items())),

        ('Variant Calling tasks',
         list(paip.pipelines.variant_calling.__dict__.items())),

        ('Ion Torrent tasks',
         list(paip.pipelines.ion_torrent.__dict__.items())),

        ('Quality Control tasks',
         list(paip.pipelines.quality_control.__dict__.items())),

        ('Annotation and Report tasks',
         list(paip.pipelines.annotation_and_report.__dict__.items())),

        ('CNV Calling tasks',
         list(paip.pipelines.cnv_calling.__dict__.items())),

        ('Other tasks',
         list(paip.pipelines.__dict__.items())),
    ])

    tasks = OrderedDict()

    for task_group_name, object_list in objects.items():
        tasks[task_group_name] = []

        for task_name, klass in sorted(object_list):
            if isinstance(klass, luigi.task_register.Register):
                tasks[task_group_name].append(task_name)

    return tasks
