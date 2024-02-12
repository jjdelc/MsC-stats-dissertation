import os
import typing as t
from pathlib import Path
from collections import defaultdict

import pandas as pd
import pyreadstat

from modules import MODULE_NAMES


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
    """
    This class will find all the .sav files from the unzipped ENAHO survey
    files and make them available year, modules and columns.
    """

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self._files = {}

    def read_files(self):
        """
        For all the survey SPSS files in the .root_dir, return the handlers
        for all of them.

        Note that this will only read the header of the files, not the full
        bodies of them in order to remain speedy.
        """
        spss_files = self.find_spss_files()
        spss_handlers = self.load_spss_files(spss_files)
        self._files = spss_handlers

    def find_spss_files(self) -> t.Dict[str, t.List[str]]:
        """
        Traverses all the deeply nested directories inside the .root_dir,
        since each of the first level directories has the name corresponding
        to the year, it will look for all the .sav files inside.

        This contains the heuristics to filter out only the survey files
        and not many of the other adjacent .sav files that come in the zip
        files provided.

        ./
            <year>/
                <module>/
                    ENAHO...sav
                    other_file.sav
                    other_files.etc

        Returns a dictionary keyed by year with a list of filenames.
        """
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

                        # File 300A is a special annex for parents satisfaction
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

                        spss_filepath = os.path.join(module_path, filename)
                        spss_files[year_dir].append(spss_filepath)
                        break

        return spss_files

    @property
    def years(self) -> t.List[str]:
        return sorted(self._files)

    @property
    def available_modules(self) -> t.List[str]:
        modules = set()
        for year in self.years:
            modules.update(self._files[year])
        return sorted(modules)

    def modules(self, year) -> t.List[str]:
        return sorted(self._files[year])

    def strip_module(self, filename: str) -> str:
        """
        We know that module names have the following format:
            XXX-ModuloYY
        Where YY is the module we want to extract.
        """
        module_name = Path(filename).parent.name
        return module_name.split("Modulo")[-1]

    def load_spss_files(self, spss_files: t.Dict[str, t.List[str]]) -> t.Dict[
        str, t.Dict[str, SurveyFile]]:
        spss_handlers = {}
        for year, filenames in spss_files.items():
            year_handlers = {}
            for fn in filenames:
                module = self.strip_module(fn)
                year_handlers[module] = SurveyFile(year, module, fn)

            spss_handlers[year] = year_handlers
        return spss_handlers

    def get_file(self, year: t.Union[str, int],
                 module: t.Union[str, int]) -> SurveyFile:
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

    def data_columns(self, module, q_names: t.List[str],
                     include_demographics=True) -> pd.DataFrame:
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
