from collections import defaultdict

import pandas as pd


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

        data = {"modulo": all_modules}
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

        data = {"modulo": all_modules}
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
        columns_by_year = []
        all_columns = set()
        for year in self.survey.years:
            year_file = self.survey.get_file(year, module)
            columns_by_year.append((year, year_file.meta.column_names))
            all_columns.update(year_file.meta.column_names)

        all_columns = sorted(all_columns)
        data = []
        for year, cols in columns_by_year:
            cols = set(cols)
            year_row = [year] + ["X" if c in cols else "" for c in all_columns]
            data.append(year_row)

        df = pd.DataFrame(data=data, columns=["year"] + all_columns)
        return df

    def common_columns(self, module):
        """
        The idea is to know which are the columns that are
        present in all years surveys.
        """
        columns_by_year = []
        all_columns = set()
        for year in self.survey.years:
            year_survey = self.survey.get_file(year, module)
            year_cols = year_survey.meta.column_names
            all_columns.update(year_cols)
            columns_by_year.append(year_cols)

        for year_cols in columns_by_year:
            all_columns = all_columns.intersection(year_cols)

        return sorted(all_columns)

    def all_questions(self):
        questions_by_module = defaultdict(dict)

        for year in self.survey.years:
            modules_for_year = self.survey.modules(year)
            for module in modules_for_year:
                survey_file = self.survey.get_file(year, module)
                col_2_label = survey_file.meta.column_names_to_labels
                col_2_label = {k.upper(): (v or "").replace("\n", "") for k, v
                               in col_2_label.items()}
                questions_by_module[module].update(col_2_label)

        data = [["Module", "Q. Name", "Q. Label"]]
        for module, question_labels in questions_by_module.items():
            for q_name, q_label in sorted(question_labels.items()):
                row = [module, q_name, q_label]
                data.append(row)

        from io import StringIO
        fh = StringIO()
        from csv import writer
        w = writer(fh)
        w.writerows(data)
        fh.seek(0)
        return fh

    def all_filenames(self, filter_year=None, filter_module=None):
        """
        This will list all the .pdf files used for each survey.
        This may help see any weird file outside the pattern of files.
        """
        result = []
        survey = self.survey
        for year in survey.years:
            for module in survey.modules(year):
                survey_file = survey.get_file(year, module)
                result.append((year, module, survey_file.filename))

        df = pd.DataFrame(data=result, columns=["year", "module", "filename"])

        if filter_year:
            df = df[df.year == filter_year]

        if filter_module:
            df = df[df.module == filter_module]

        return df.sort_values(by=["module", "year"])
