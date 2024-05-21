#!/usr/bin/env python3

from code.survey import SurveyReader
from code.reporter import Reporter


DATA_DIR = "../ENAHO/"


if __name__ == '__main__':
    survey = SurveyReader(DATA_DIR)
    survey.read_files()
    reporter = Reporter(survey)
    yearly_modules = reporter.yearly_modules()
    yearly_cols = reporter.modules_dims("cols")
    filenames = reporter.all_filenames()
    # all_questions_report = reporter.all_questions()
    s_file = survey.get_file(2022, 3)
    # stack = survey.data_columns("03", ["P300N", "P300I"])
    import pdb;pdb.set_trace()
