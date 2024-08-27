from survey.survey import SurveyReader
from reporter import Reporter

# Folder with the survey SPSS files
DATA_DIR = "../ENAHO"

# For the sanity checks will verify years 2014 through 2023
STUDY_YEARS = {str(y) for y in range(2014, 2024)}

survey = SurveyReader(DATA_DIR, include_years=STUDY_YEARS)
survey.read_files()

reporter = Reporter(survey)
yearly_modules = reporter.yearly_modules()

# print(yearly_modules)

# print(reporter.all_filenames().to_string())

yearly_cols = reporter.modules_dims("cols")
yearly_rows = reporter.modules_dims("rows")

# print(yearly_rows)

print(reporter.variables_per_module("34"))
