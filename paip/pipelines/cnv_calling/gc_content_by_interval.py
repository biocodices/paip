from paip.task_types import CohortTask


class GCContentByInterval(CohortTask):
    """
    Takes the panel BED file and calculates the GC content by interval using
    GATK's GCContentByInterval module.
    """
    OUTPUT = ['DATA.locus_GC.txt', 'extreme_gc_targets.txt']
    SUBDIR = 'xhmm_run'
    REQUIRES = []

    def run(self):
        gc_by_interval_file = self.output()[0].path

        # First step: run GATK and produce a 'GC content by interval' file
        program_name = 'gatk3 GCContentByInterval'
        program_options = {'outfile': gc_by_interval_file}
        self.run_program(program_name, program_options)

        # Second step: take the file produced above and keep only
        # the interval names with extreme GC content:
        program_name = 'awk extreme_GC_targets'
        program_options = {
            'gc_content_by_interval': gc_by_interval_file,
            'outfile': self.output()[1].path,
        }
        self.run_program(program_name, program_options)

