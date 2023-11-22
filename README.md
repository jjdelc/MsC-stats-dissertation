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

```


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
