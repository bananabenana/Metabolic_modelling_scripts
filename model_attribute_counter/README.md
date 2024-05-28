# Model attribute counter
This script will calculate the total number of reactions, genes and metabolites of genome-scale metabolic models. It is parallelised so should process 1000's of metabolic models rapidly. 

## Overview and process
1. The script takes input directory of metabolic models (file format: `.json`, `.xml`) 
2. Counts number of reactions, genes and metabolites encoded in parallel
3. Outputs file as table


## Usage
To use, run:
```
python count_model_attributes.py -d input_directory_of_models -o model_attribute_counts.tsv -p 8
```
`-d` refers to input directory containing models

`-o` refers to output filename

`-p` refers to number of parallel processes based on CPU threads

## Dependancies
- unix environment with basename, dirname and getopts, pandas, cobra

## Installation
The best way to install this is to download this directory and run the script directly in command line.

## Authors
- Ben Vezina (https://scholar.google.com/citations?user=Rf9oh94AAAAJ&hl=en)
