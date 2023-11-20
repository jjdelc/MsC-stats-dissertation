#!/bin/bash

for year in {2010..2022}; do
  cd $year
  for zip in *.zip; do
    unzip -o "$zip" && rm "$zip"
  done
  cd ..
done
