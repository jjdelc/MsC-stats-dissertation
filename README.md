# MsC-stats-dissertation

Files to download and process data for MsC Applied Statistics dissertation.

This repo allows to download the ENAHO[1] survey data from:

> https://proyectos.inei.gob.pe/microdatos/Consulta_por_Encuesta.asp


This uses Jupyter Notebook:

```
python3.10 -m venv venv 
. ./venv/bin/activate
pip install -U pip
pip install jupyter
pip install pandas
pip install matplotlib
pip install seaborn
pip install pyreadstat
pip install savReaderWriter
pip install statsmodels

```

Sample usage to verify that data has loaded correctly:
```
from survey import SurveyReader
from reporter import Reporter
survey = SurveyReader("../ENAHO/")
survey.read_files()
reporter = Reporter(survey)
yearly_modules = reporter.yearly_modules()
yearly_cols = reporter.modules_dims("cols")
yearly_rows = reporter.modules_dims("rows")
```

Ensure that all years have files for all modules
Check that all surveys' .sav filename is reasonable
Check rows and columns for all surveys that they are within similar size
Check all the questions made yearly for a module
Check all the common questions for a module in all years
Report of all questions labels
Filtering .sav files per module
Reading data dictionary
Translating questions using Google Docs translate feature (Via CSV, spreadsheet)
Modules that need special treatment bc files are split


Statsmodel
https://www.statsmodels.org/stable/gettingstarted.html
For linear regressions

ENAHO papers
https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=Peru+ENAHO&btnG=


## Caveats

### Incompatible libraries

Library savReaderWriter is not compatible with python 3.10
So it needs a bit of manual adjusting to change an import
for `collections.Iterator` to `collections.abc.Iterator`.

### Interrupted downloads

Sometimes, the downloads get aborted from the server, so when
it seems that it all finished, turns out some files are missing.

Using the Reporter class helps to identify the missing entries and
re-download manually.


### Inconsistency in file structure:

Year 2015 needs manual unzipping because most of the module
files are not inside a directory.

Something along these lines is needed:

```
for zip_file in *.zip; do
    base_name="${zip_file%%.*}" # Extract filename without extension

    # Create a directory with the filename if it doesn't exist
    if [ ! -d "$base_name" ]; then
        mkdir "$base_name"
    fi

    # Unzip the files into the directory or directly into the current directory
    unzip -d "$base_name" "$zip_file" || unzip "$zip_file"

    # Remove the zip file
    #rm "$zip_file"
done
```

And then manually fix a few folders manually.



[1] ENAHO - Encuesta Nacional de Hogares



# Literacy review

Poverty, Household Structure and Consumption of Foods Away from Home in Peru in 2019: A Cross-Sectional Study 
https://www.mdpi.com/2304-8158/11/17/2547


Households with and without the presence of adolescents, probability of expenditure on food consumed away from home, according to
ENAHO 2021: a cross-sectional study [version 1; peer review: 1 not approved] 
https://f1000research.com/articles/12-1296

Inequalities in access to safe drinking water in Peruvian households according to city size: an analysis from 2008 to 2018
https://link.springer.com/article/10.1186/s12939-021-01466-7

Measuring Out-of-pocket Payment, Catastrophic Health Expenditure and the Related Socioeconomic Inequality in Peru: A Comparison Between 2008 and 2017
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7411247/