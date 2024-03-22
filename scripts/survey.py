import typing as t
from pathlib import Path
from collections import defaultdict

import pandas as pd
import pyreadstat

from modules import MODULE_NAMES
from find_files import find_spss_files


class SurveyFile:
    """
    This class holds an individual SPSS file.
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

    def labels_for_question(self, question_name: str) -> t.Dict[str, str]:
        """
        Given a question name, return the dictionary of the labels for each
        of the categorical answers of it.
        """
        return self._meta.variable_value_labels[question_name]


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
        For all the survey SPSS files in the .root_dir, load their handlers.

        Note that this will only read the header of the files, not the full
        bodies of them in order to remain speedy.
        """
        spss_files = find_spss_files(self.root_dir)
        spss_handlers_by_year = self.load_spss_files(spss_files)
        self._files = spss_handlers_by_year

    @property
    def years(self) -> t.List[str]:
        """
        Returns list of sorted years (as strings) that this survey contains
        based on the available directories inside ENAHO root_dir.
        """
        return sorted(self._files)

    def modules_per_year(self) -> t.Dict[str, t.Set[str]]:
        """
        Returns a dictionary keyed by year, with the set of available modules
        for each year.
        """
        years = self.years
        yearly_modules = {y: set(self.modules(y)) for y in years}
        return yearly_modules

    def available_modules(self) -> t.List[str]:
        """
        Returns a sorted list of the modules codes (strings) that this survey
        contains through all the years. This is the accumulation of present
        modules.
        """
        modules = set()
        for year in self.years:
            modules.update(self._files[year])
        return sorted(modules)

    def modules(self, year) -> t.List[str]:
        """
        Returns the sorted list of string module codes available in a given year
        """
        return sorted(self._files[year])

    def module_from_filename(self, filename: str) -> str:
        """
        We know that module names have the following format:
            XXX-ModuloYY
        Where YY is the module we want to extract.
        """
        module_name = Path(filename).parent.name
        return module_name.split("Modulo")[-1]

    def load_spss_files(
            self, spss_files: t.Dict[str, t.List[str]]
    ) -> t.Dict[str, t.Dict[str, SurveyFile]]:
        """
        Returns a doubly nested dictionary. First by year, and then by module
        pointing to the associated SurveyFile.
        """
        yearly_spss_handlers = {}
        for year, filenames in spss_files.items():
            year_handlers = {}
            for fn in filenames:
                module = self.module_from_filename(fn)
                year_handlers[module] = SurveyFile(year, module, fn)

            yearly_spss_handlers[year] = year_handlers
        return yearly_spss_handlers

    def get_file(
            self, year: t.Union[str, int], module: t.Union[str, int]
    ) -> SurveyFile:
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

    def data_columns(
            self, module, q_names: t.List[str],
            include_demographics: bool = True
    ) -> pd.DataFrame:
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
            segments.append(survey_file.data[columns])

        result = pd.concat(segments, ignore_index=True)
        return result

    def value_labels(self, module: str, q_names: t.List[str]) -> t.Dict[
        str, t.Dict[str, str]]:
        """
        Given a list of question name strings (narrowed down by their associated
        module). Return a dictionary keyed by question containing all the
        labels associated with each question.

        {
            Q_1: {
                1: "label for answer coded 1 in Q1",
                2: "label for answer coded 2 in Q1",
            },
            Q_2: {
                1: "label for answer coded 1 in Q2",
                2: "label for answer coded 2 in Q2",
            },
        }
        """
        q_name_labels = defaultdict(list)
        # This will raise error if requesting questions for the wrong module
        module_files = [self.get_file(year, module) for year in self.years]

        for mod_file in module_files:
            # Accumulate all the values for these questions through all the
            # years we want to detect if they changed.
            for q_name in q_names:
                q_name_labels[q_name].append(
                    mod_file.labels_for_question(q_name))

        final_q_names = {}
        for q_name, yearly_labels in q_name_labels.items():
            q_labels = {}
            # Here we should be detecting if they changed or not.
            for y_label in yearly_labels:
                q_labels.update(y_label)
            final_q_names[q_name] = q_labels

        return final_q_names
