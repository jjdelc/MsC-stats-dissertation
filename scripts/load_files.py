#!/usr/bin/env python3

import os
import sys
import pandas as pd
import pyreadstat
import savReaderWriter as spss
from pathlib import Path
from collections import defaultdict


DATA_DIR = "./ENAHO/"


class SurveyFile:
    """
    This class holds a individual SPSS file.
    Will do a bare minimal read by default, and only
    do a full file read if required for a data frame.
    """

    ENC = "latin-1"  # Files encoding

    def __init__(self, year, module, filepath):
        self.filepath = filepath
        self.filename = Path(filepath).name
        self.year = year
        self.module = module
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
            self._meta = pyreadstat.read_sav(self.filepath, metadataonly=True)[1]
        return self._meta

    @property
    def sav_file(self):
        if self._sav is None:
            # en_US.ISO8859-1
            self._sav = spss.SavReader(self.filepath, rawMode=True, ioUtf8=False)
        return self._sav

    def labels(self):
        return {
            n.decode(self.ENC): l.decode(self.ENC)
            for n, l in self.sav_file.varLabels.items()
        }

    def names(self):
        return [n.decode(self.ENC) for n in self.sav_file.varNames]

    @property
    def shape(self):
        """
        This returns Shape() class that contains attributes
        .nrows and ncols
        """
        return self.sav_file.shape


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


                        spss_files[year_dir].append(os.path.join(module_path, filename))
                        break

        return spss_files

    @property
    def years(self):
        return sorted(self._files)

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

    def get_file(self, year, module):
        if not isinstance(year, str):
            year = str(year)  # "2022"
        
        if not isinstance(module, str):
            module = "{:02}".format(module)  # "07"

        return self._files[year][module]



class Reporter:
    def __init__(self, survey):
        self.survey = survey

    def yearly_modules(self):
        """
        Returns a Pandas DataFrame indicating
        which modules are present in each year.
        """
        years = self.survey.years
        yearly_modules = {y: set(self.survey.modules(y)) for y in years}
        all_modules = list(yearly_modules.values())
        all_modules = {val for sublist in all_modules for val in sublist}
        all_modules = sorted(all_modules)

        data = {"module": all_modules}
        data.update({y: [] for y in years})
        for y in years:
            year_data = data[y]
            for m in all_modules:
                year_data.append("X" if m in yearly_modules[y] else "")

        df = pd.DataFrame(data=data)
        return df


    def modules_dims(self, dimension="cols"):
        """
        Returns a Pandas DataFrame indicating the requested
        dimension for each module survey.
        """
        years = self.survey.years
        yearly_modules = {y: set(self.survey.modules(y)) for y in years}
        all_modules = list(yearly_modules.values())
        all_modules = {val for sublist in all_modules for val in sublist}
        all_modules = sorted(all_modules)

        data = {"module": all_modules}
        data.update({y: [] for y in years})
        for y in years:
            year_data = data[y]
            for m in all_modules:
                meta = self.survey.get_file(y, m).meta
                value = meta.number_columns if dimension == "cols" else meta.number_rows
                year_data.append(value)


        df = pd.DataFrame(data=data)
        return df


    def variables_per_module(self, module):
        """
        Given the survey and a module, indicate the common
        and missing variables per year.
        This returns a DataFrame to visualize which variables
        are common and what changed across years.
        """
        raise NotImplementedError()



if __name__ == '__main__':
    survey = SurveyReader(DATA_DIR)
    survey.read_files()
    reporter = Reporter(survey)
    yearly_modules = reporter.yearly_modules()
    yearly_cols = reporter.modules_cols()
    import pdb;pdb.set_trace()
