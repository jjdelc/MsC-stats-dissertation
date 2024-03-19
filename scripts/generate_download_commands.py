#!/usr/bin/env python3

"""
Use this script to download the ENAHO survey files per year into a folder per year.
Each folder will contain the zip files for the SPSS files and a urls.txt files with the
URLs of the downloaded files.

The output will be a print of `wget` commands to download all the files.

Here's the usage to download files from years 2010 to 2022:


[ENAHO] python3 ./stripurls.py 2022 2021 2020 2019 2018 2017 2016 2015 2014 2013 2012 2011 2010                                                                 <freya>
INFO:root:Processing year: 2022
INFO:root:Processing year: 2021
INFO:root:Processing year: 2020
INFO:root:Processing year: 2019
INFO:root:Processing year: 2018
INFO:root:Processing year: 2017
INFO:root:Processing year: 2016
INFO:root:Processing year: 2015
INFO:root:Processing year: 2014
INFO:root:Processing year: 2013
INFO:root:Processing year: 2012
INFO:root:Processing year: 2011
INFO:root:Processing year: 2010
wget -i ./2016/urls.txt -P 2022
wget -i ./2016/urls.txt -P 2021
wget -i ./2016/urls.txt -P 2020
wget -i ./2016/urls.txt -P 2019
wget -i ./2016/urls.txt -P 2018
wget -i ./2016/urls.txt -P 2017
wget -i ./2016/urls.txt -P 2016
wget -i ./2015/urls.txt -P 2015
wget -i ./2014/urls.txt -P 2014
wget -i ./2013/urls.txt -P 2013
wget -i ./2012/urls.txt -P 2012
wget -i ./2011/urls.txt -P 2011
wget -i ./2010/urls.txt -P 2010
"""

import sys
import logging
from os.path import join
from urllib.parse import urljoin
from urllib.request import urlopen, Request

logging.basicConfig(level=logging.INFO)

# Contant of the INEI domain where all files are placed
BASE_URL = "https://proyectos.inei.gob.pe/"

# This is the path to make a request to fetch the table
# of files available for each year.
FETCH_URL = "/microdatos/cambiaPeriodo.asp"

# This is the required payload that needs to have the
# year added to obtain the files table from FETCH_URL
PAYLOAD = "bandera=1&_cmbEncuesta=Condiciones%20de%20Vida%20y%20Pobreza%20-%20ENAHO&_cmbAnno={}&_cmbTrimestre=55"

# The folder where the data will be downloaded
DATA_PATH = "./ENAHO/"


def strip_link(line):
    """
    For a matching line in the HTML table, strip the SPSS
    .zip file link from the <a href> tag.
    We can do this because we know the way the HTML is formatted
    wich each <a> tag on a separate line.

        <a href="/...spss...zip">...

    """
    href = line.split('"')[1]
    return urljoin(BASE_URL, href)


def process_file(fh):
    """
    Given a file-like object, in this case an Http Response
    object, process only those lines that contain "/SPSS/"
    on it. This hints that it is the HTML line that contains
    the file link.

    Collect and return all these links
    """

    links = []
    for line in fh.readlines():
        # The INEI website returns HTML using in `latin-1` encoding
        line = line.decode("latin-1")
        if "/SPSS/" in line:
            links.append(strip_link(line))
    return links


def build_request(year):
    """
    Builds an HTTP Request POST object to download the table
    containing the given year's survey files.
    """
    request = Request(
        url=urljoin(BASE_URL, FETCH_URL),
        data=PAYLOAD.format(year).encode("utf-8"),
        method="POST")

    return request


def write_url_files(urls_per_year):
    """
    Given a dictionary of urls per year, write them in the
    {YEAR}/urls.txt file for each year,

    Returns the list of files.
    """
    year_files = []
    for year, urls in urls_per_year.items():
        output_file = join(DATA_PATH, "{}/urls.txt".format(year))
        with open(output_file, "w") as fh:
            fh.write("\n".join(urls))
            fh.write("\n")  # Extra EOL
        year_files.append((year, output_file))
    return year_files


def download_year_files(year_files):
    """
    Returns the list of `wget` commands to
    download these files.
    """

    # -i argument for the URLs input file
    # -P parameter for output directory
    WGET = "wget -i {} -P {}"
    commands = []
    for year, year_file in year_files:
        commands.append(WGET.format(year_file, join(DATA_PATH, year)))
    
    return commands


def fetch_yearly_spss_urls(years):
    """
    Given a list of years, return a dictionary keyed by each
    year that contains the list of the URLs for the survey's
    associated SPSS files.

    For each year, makes an HTTP request and parses the response
    body searching only for the SPSS file links.
    """
    urls_per_year = {}

    for year in years:
        logging.info("Processing year: {}".format(year))
        resp = urlopen(build_request(year))
        urls_per_year[year] = process_file(resp)

    return urls_per_year


if __name__ == "__main__":
    years = sys.argv[1:]

    # Extract URLs from survey website    
    urls_per_year = fetch_yearly_spss_urls(years)

    # Prepare download commands
    year_files = write_url_files(urls_per_year)
    download_commands = download_year_files(year_files)
    print("\n".join(download_commands))
