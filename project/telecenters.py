"""
Computation of use of telecenters per domain in Peru 2023 using ENAHO database.
"""

from survey.survey import SurveyReader
from constants import STUDY_YEARS

import pandas as pd
DATA_DIR = "../ENAHO"

survey = SurveyReader(DATA_DIR, include_years=STUDY_YEARS)
survey.read_files()

# We want module 01 to filter only completed surveys
q_names_01 = ["RESULT"]
module_01 = survey.data_columns("01", q_names_01, include_demographics=False)

# Internet use questions
q_names_03 = [
    "P314A",  # Used internet in the last month
    "P314B$4",  # Used internet in telecenter
]
internet_qs = survey.data_columns("03", q_names_03, include_demographics=True)

# Merge with module 01 that allows us to filter only the survey answers
internet_qs = pd.merge(internet_qs, module_01, on=["HOUSE_KEY"], how="left")

# That have been completed the survey `RESULT == 1`
internet_qs = internet_qs[internet_qs["RESULT"] == 1]

# Population per domain, to obtain percents of population that uses telecenter
population_per_domain = internet_qs['DOMINIO'].value_counts().reset_index(name='count')
population_per_domain = pd.DataFrame(population_per_domain)

# Computer population that uses telecenters per domain
uses_telecenter = (internet_qs["P314B$4"] == 4) & (internet_qs["P314A"] == 1)
internet_qs["uses_telecenter"] = uses_telecenter.astype(int)
respondents_telecenter = internet_qs[internet_qs["uses_telecenter"] == 1]
telecenter_per_domain = respondents_telecenter['DOMINIO'].value_counts().reset_index(name='count')
telecenter_per_domain = pd.DataFrame(telecenter_per_domain)

# Combine with population per domain
telecenter_per_domain["population"] = population_per_domain["count"]

# Compute percents
telecenter_per_domain["pct"] = 100*telecenter_per_domain["count"] / telecenter_per_domain["population"]
percent_uses_telecenter = 100*len(internet_qs[internet_qs["uses_telecenter"] == 1])/len(internet_qs)

print(f"Total respondents {len(internet_qs)}")
print(f"Total uses telecenter {percent_uses_telecenter}")
print(telecenter_per_domain)
