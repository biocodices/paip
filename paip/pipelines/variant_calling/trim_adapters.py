import re

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import CheckFastqs
from paip.helpers.create_cohort_task import create_cohort_task


class TrimAdapters(SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample. Trims the adapters of those reads files and generates
    new fastq files.
    """
    REQUIRES = CheckFastqs
    OUTPUT = {'forward_reads': 'R1.trimmed.fastq.gz',
              'reverse_reads': 'R2.trimmed.fastq.gz'}

    def run(self):
        fwd_tmp_manager = self.output()['forward_reads'].temporary_path()
        rev_tmp_manager = self.output()['reverse_reads'].temporary_path()
        # These are Python context managers that handle the renaming of the
        # temporary path on __exit__. See the _Manager class at link [1].
        # I need to edit the _temp_path that they use because cutadapt expects
        # a filename ending in ".gz", otherwise it will not compress its
        # output, but by default Luigi produces temporary paths that end in
        # "-luigi-tmp-<some_random_number>".
        fwd_tmp_manager._temp_path = self.fix_temp_path(fwd_tmp_manager._temp_path)
        rev_tmp_manager._temp_path = self.fix_temp_path(rev_tmp_manager._temp_path)

        with fwd_tmp_manager as temp_fwd, rev_tmp_manager as temp_rev:
            program_name = self.trim_software
            program_options = {
                'forward_reads': self.input()['forward_reads'].path,
                'reverse_reads': self.input()['reverse_reads'].path,
                'forward_output': temp_fwd,
                'reverse_output': temp_rev,
            }
            self.run_program(program_name, program_options)

    def fix_temp_path(self, temp_path):
        """
        Take a luigi temporary path like "Sample.fastq.gz-luigi-tmp-1234"
        and move the "tmp" chunk before the ".fastq.gz" part, to return
        something like "Sample.-luigi-tmp-1234.fastq.gz".
        """
        temp_chunk = re.search(r'-luigi-tmp-\d+$', temp_path).group(0)
        clean_path = temp_path.replace(temp_chunk, '')
        return clean_path.replace('.fastq.gz', f'.{temp_chunk}.fastq.gz')


TrimAdaptersCohort = create_cohort_task(TrimAdapters)

# [1] https://luigi.readthedocs.io/en/stable/_modules/luigi/target.html#FileSystemTarget.temporary_path
