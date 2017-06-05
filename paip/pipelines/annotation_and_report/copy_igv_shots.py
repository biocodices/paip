import os
import shutil
from glob import glob
import logging

import luigi

from paip.task_types import SampleTask
from paip.pipelines.annotation_and_report import TakeIGVSnapshots
from paip.helpers.create_cohort_task import create_cohort_task


logger = logging.getLogger(__name__)


class CopyIGVShots(SampleTask):
    REQUIRES = TakeIGVSnapshots

    def output(self):
        img_dir = self.path('report_{}/images/igv'.format(self.sample),
                            prefix=False)
        return luigi.LocalTarget(img_dir)

    def run(self):
        snapshots_dir = self.input()['snapshots_dir'].path
        destination_dir = self.output().path

        os.makedirs(destination_dir, exist_ok=True)

        images_to_copy = glob('{}/*'.format(snapshots_dir))
        for image in images_to_copy:
            shutil.copy2(image, destination_dir)

        logger.warning('Copied {} images to {}'
                       .format(len(images_to_copy), destination_dir))


CopyIGVShotsCohort = create_cohort_task(CopyIGVShots)

