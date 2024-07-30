import os
import typing as t
from collections import defaultdict


def find_spss_files(root_dir) -> t.Dict[str, t.List[str]]:
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
    for year_dir in os.listdir(root_dir):
        if len(year_dir) != 4:
            # Not a year, skip it
            continue

        year_path = os.path.join(root_dir, year_dir)
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
                        "700A", "700B", "700a", "700b", "613", "613H"
                    ]
                    if any(x in filename for x in excluded_files):
                        continue

                    spss_filepath = os.path.join(module_path, filename)
                    spss_files[year_dir].append(spss_filepath)
                    break

    return spss_files
