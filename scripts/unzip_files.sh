#!/bin/bash

cd ../ENAHO
for year in {2007..2023}; do
  cd $year
  for zip in *.zip; do
    unzip -o "$zip" && rm "$zip"
  done
  cd ..
done
