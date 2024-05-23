#!/bin/bash

cd ../ENAHO
for year in {2004..2006}; do
  cd $year
  for zip in *.zip; do
    unzip -o "$zip" && rm "$zip"
  done
  cd ..
done
