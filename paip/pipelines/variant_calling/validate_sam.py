import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import FixReadGroups
from paip.helpers.create_cohort_task import create_cohort_task


class ValidateSam(SampleTask):
    """
    Takes a SAM and checks its valid. If it is, creates an empty file with the
    same name as the input SAM plus '.is_valid'.
    """
    REQUIRES = FixReadGroups
    OUTPUT_RENAMING = ('.sam', '.sam.validation_result')

    def run(self):
        with self.output().temporary_path() as temp_out:
            program_name = 'picard ValidateSamFile'
            program_options = {
                'input_sam': self.input().path,
                'output_txt': temp_out,
            }
            self.run_program(program_name, program_options)

        with open(self.output().path) as f:
             validation_file_contents = f.read()

        if 'No errors found' not in validation_file_contents:
            raise InvalidSamException('SAM file appears not to be valid. '
                                      'Maybe the read groups fix went wrong? '
                                      f'Check: {self.input().path}')


class InvalidSamException(Exception): pass


ValidateSamCohort = create_cohort_task(ValidateSam)
