import os
from pathlib import Path
from collections import defaultdict
from typing import List

import pandas as pd
import pyreadstat

MODULE_NAMES = {
    "01": {
        "modulo": "Características de la Vivienda y del Hogar",
        "module": "Housing and Household Characteristics"
    },
    "02": {
        "modulo": "Características de los Miembros del Hogar",
        "module": "Household Members Characteristics"
    },
    "03": {
        "modulo": "Educación",
        "module": "Education"
    },
    "04": {
        "modulo": "Salud",
        "module": "Health"
    },
    "05": {
        "modulo": "Empleo e Ingresos",
        "module": "Employment and Income"
    },
    "07": {
        "modulo": "Gastos en Alimentos y Bebidas (Módulo 601)",
        "module": "Food and Beverage Expenditures (Module 601)"
    },
    "08": {
        "modulo": "Instituciones Beneficas",
        "module": "Charitable Institutions"
    },
    "09": {
        "modulo": "Mantenimiento de la Vivienda",
        "module": "Housing Maintenance"
    },
    "10": {
        "modulo": "Transportes y Comunicaciones",
        "module": "Transportation and Communications"
    },
    "11": {
        "modulo": "Servicios a la Vivienda",
        "module": "Housing Services"
    },
    "12": {
        "modulo": "Esparcimiento, Diversion y Servicios de Cultura",
        "module": "Recreation, Entertainment, and Cultural Services"
    },
    "13": {
        "modulo": "Vestido y Calzado",
        "module": "Clothing and Footwear"
    },
    "15": {
        "modulo": "Gastos de Transferencias",
        "module": "Transfer Expenditures"
    },
    "16": {
        "modulo": "Muebles y Enseres",
        "module": "Furniture and Equipment"
    },
    "17": {
        "modulo": "Otros Bienes y Servicios",
        "module": "Other Goods and Services"
    },
    "18": {
        "modulo": "Equipamiento del Hogar",
        "module": "Household Appliances"
    },
    "22": {
        "modulo": "Producción Agrídcola",
        "module": "Agricultural Production"
    },
    "23": {
        "modulo": "Subproductos Agricolas",
        "module": "Agricultural By-Products"
    },
    "24": {
        "modulo": "Producción Forestal",
        "module": "Forest Production"
    },
    "25": {
        "modulo": "Gastos en Actividades Agricolas y/o Forestales",
        "module": "Expenditures on Agricultural and/or Forestry Activities"
    },
    "26": {
        "modulo": "Producción Pecuaria",
        "module": "Livestock Production"
    },
    "27": {
        "modulo": "Subproductos Pecuarios",
        "module": "Livestock By-Products"
    },
    "28": {
        "modulo": "Gastos en Actividades Pecuarias",
        "module": "Expenditures on Livestock Activities"
    },
    "34": {
        "modulo": "Sumarias (Variables Calculadas)",
        "module": "Summaries (Calculated Variables)"
    },
    "37": {
        "modulo": "Programas Sociales (Miembros del Hogar)",
        "module": "Social Programs (Household Members)"
    },
    "77": {
        "modulo": "Ingresos del Trabajador Independiente",
        "module": "Self-Employed Income"
    },
    "78": {
        "modulo": "Bienes y Servicios de Cuidados Personales",
        "module": "Personal Care Goods and Services"
    },
    "84": {
        "modulo": "Participación Ciudadana",
        "module": "Citizen Participation"
    },
    "85": {
        "modulo": "Gobernabilidad, Democracia y Transparencia",
        "module": "Governance, Democracy, and Transparency"
    }
}


class SurveyFile:
    """
    This class holds a individual SPSS file.
    Will do a bare minimal read by default, and only
    do a full file read if required for a data frame.
    """

    ENC = "latin-1"  # Files' encoding

    def __init__(self, year, module, filepath):
        self.filepath = filepath
        self.filename = Path(filepath).name
        self.year = year
        self.module = module
        self.description = MODULE_NAMES[module]["module"]
        self._sav = None
        self._meta = None
        self._data = None

    def __repr__(self):
        return "<SurveyFile: {} Module: {}>".format(self.year, self.module)

    @property
    def data(self):
        if self._data is None:
            data, meta = pyreadstat.read_sav(self.filepath)
            self._data = data
            self._meta = meta
        return self._data

    @property
    def meta(self):
        if self._meta is None:
            self._meta = pyreadstat.read_sav(self.filepath, metadataonly=True)[
                1]
        return self._meta


class SurveyReader:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self._files = {}

    def read_files(self):
        spss_files = self.find_spss_files()
        spss_handlers = self.load_spss_files(spss_files)
        self._files = spss_handlers

    def find_spss_files(self):
        spss_files = defaultdict(list)

        # Iterate over self.root_dir
        for year_dir in os.listdir(self.root_dir):
            if len(year_dir) != 4:
                # Not a year, skip it
                continue

            year_path = os.path.join(self.root_dir, year_dir)
            if os.path.isdir(year_path):

                # Inside each year, iterate over the module folders
                for module_name in os.listdir(year_path):
                    module_path = os.path.join(year_path, module_name)
                    if not os.path.isdir(module_path):
                        continue

                    # For each module folder, find the first(only) .sav file
                    for filename in os.listdir(module_path):
                        # Some heuristics to determine the correct .sav file
                        # to read on each module because many directories
                        # contain extra support .sav files
                        if not filename.endswith('.sav'):
                            continue

                        if "AGROPECUARIO" in filename:
                            continue
                        if "ENAHO-TABLA" in filename:
                            continue

                        # File 300A is an special annex for parents satisfaction
                        # about childrens education
                        # 602A contains questions for kids below 14 about meals
                        # obtained from beneficiaries outside of home
                        # 2000A are details about fish livestock activities
                        # 700A are details about food help obtained (if any)
                        # 700B are details about non-food help obtained (if any)
                        excluded_files = [
                            "300A", "300a", "602A", "602a", "2000A", "2000a",
                            "700A", "700B", "700a", "700b"
                        ]
                        if any(x in filename for x in excluded_files):
                            continue

                        spss_files[year_dir].append(
                            os.path.join(module_path, filename))
                        break

        return spss_files

    @property
    def years(self):
        return sorted(self._files)

    @property
    def available_modules(self):
        modules = set()
        for year in self.years:
            modules.update(self._files[year])
        return sorted(modules)

    def modules(self, year):
        return sorted(self._files[year])

    def strip_module(self, filename):
        """
        We know that module names have the following format:
            XXX-ModuloYY
        Where YY is the module we want to extract.
        """
        module_name = Path(filename).parent.name
        return module_name.split("Modulo")[-1]

    def load_spss_files(self, spss_files):
        spss_handlers = {}
        for year, filenames in spss_files.items():
            year_handlers = {}
            for fn in filenames:
                module = self.strip_module(fn)
                year_handlers[module] = SurveyFile(year, module, fn)

            spss_handlers[year] = year_handlers
        return spss_handlers

    def get_file(self, year, module) -> SurveyFile:
        if not isinstance(year, str):
            year = str(year)  # "2022"

        if not isinstance(module, str):
            module = "{:02}".format(module)  # "07"

        return self._files[year][module]

    # These demographic columns are common in all survey files. These can be
    # used to perform joins.
    DEMOGRAPHIC_COLUMNS = [
        'AÑO', 'MES', 'CONGLOME', 'VIVIENDA', 'HOGAR', 'UBIGEO', 'DOMINIO'
    ]

    def data_columns(self, module, q_names: List[str],
                     include_demographics=True):
        """
        Returns a DataFrame with the stacking of the requested
        question for all files available.

        if `include_demographics` is True, the necessary demographics
        questions will be included.
        """
        columns = q_names[:]
        if include_demographics:
            columns = self.DEMOGRAPHIC_COLUMNS + columns
        segments = []

        for year in self.years:
            survey_file = self.get_file(year, module)
            try:
                segments.append(survey_file.data[columns])
            except KeyError:
                raise KeyError(year)

        result = pd.concat(segments, ignore_index=True)
        return result
