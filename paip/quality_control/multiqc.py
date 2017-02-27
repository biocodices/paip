from paip.task_types import CohortTask
from paip.variant_calling import AnnotateWithSnpeff
from paip.quality_control import FastQC, AlignmentMetrics


class MultiQC(CohortTask):
    """
    Expects several quality control programs to have run. Summarizes all those
    results in a single HTML report for the cohort.
    """
    OUTPUT = 'multiqc_report.html'

    def requires(self):
        tasks = [FastQC, AlignmentMetrics, AnnotateWithSnpeff]
        return [task(sample=sample, basedir=self.basedir)
                for sample in self.sample_list
                for task in tasks]

    def run(self):
        program_name = 'multiqc'
        program_options = {
            'basedir': self.basedir,
        }
        self.run_program(program_name, program_options)

