from project.survey import SurveyReader
from project.constants import DATA_DIR, STUDY_YEARS

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

survey = SurveyReader(DATA_DIR, include_years=STUDY_YEARS)
survey.read_files()
#%%
q_names_01 = [
    "P1121",  # Electric grid
    "P1141",  # House has landline
    "P1142",  # Owns Cell phone at home
    "P1144",  # Has Internet connection
    "P1145",  # Does NOT have phone/pc/internet
    "RESULT",
]
module_01 = survey.data_columns("01", q_names_01, include_demographics=False)
module_01["has_landline"] = module_01["P1141"] == 1
module_01["cellphone_at_home"] = module_01["P1142"] == 1
module_01["home_internet_connection"] = module_01["P1144"] == 1
module_01["no_equipment"] = module_01["P1145"] == 1

q_names_18 = [
    "P612N",  # Home equipment type
    "P612",  # Home equipment has
]
equipment = survey.data_columns("18", q_names_18, include_demographics=False)
equipment["has_radio_tv"] = (equipment["P612N"] <= 3) & (equipment["P612"] == 1)
equipment["has_computer"] = (equipment["P612N"] == 7) & (equipment["P612"] == 1)
aggregations_18 = {"has_radio_tv": "any", "has_computer": "any"}
equipment_per_house = pd.DataFrame(equipment.groupby("HOUSE_KEY").agg(aggregations_18))

SUMMARY_FIELDS = [
    "POBREZA",
    "INGHOG2D",  # House net income
    "LINPE",
    "LINEA",
    "ESTRSOCIAL",
    "MIEPERHO",  # Number of people in household
    "FACTOR07"
]
poverty = survey.data_columns("34", SUMMARY_FIELDS, include_demographics=False)

house_data = pd.merge(poverty, equipment_per_house, on=["HOUSE_KEY"], how="left")
house_data = pd.merge(module_01, house_data, on=["HOUSE_KEY"], how="left")

