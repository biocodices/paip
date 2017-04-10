from paip.task_types import CohortTask


class GCContentByInterval(CohortTask):
    """
    Takes the panel BED file and calculates the GC content by interval using
    GATK's GCContentByInterval module.
    """
    OUTPUT = ['DATA.locus_GC.txt', 'extreme_gc_targets.txt']
    SUBDIR = 'xhmm_run'

    def run(self):
        gc_by_interval_file = self.output()[0]

        with gc_by_interval_file.temporary_path() as tempfile:
            program_name = 'gatk GCContentByInterval'
            program_options = {'outfile': tempfile}
            self.run_program(program_name, program_options)

        # This second step takes the file produced above and filters
        # the interval names with extreme GC content into a new file:
        program_name = 'awk extreme_GC_targets'
        program_options = {
            'gc_content_by_interval': gc_by_interval_file.path,
            'outfile': 'extreme_gc_targets.txt',
        }
        self.run_program(program_name, program_options)

