# Single gene knockout/deletion analysis

This script runs a user-friendly version of single_gene_deletion() function from COBRApy. Each gene within a metabolic model will be iteratively deleted one by one, then growth tested on either a supplied or custom in silico growth media. If model growth (biomass) is above ≥ 0.0001, growth has taken place and the resulting gene is NOT essential in that growth media environment. This allows the user to get an overview of which genes are essential or non-essential.

## Overview and process
1. The script takes input directory contaning metabolic model file/s and reference model file (model file formats: `.xml`, `.json`, `.sbml`) 
2. Initialises model on growth media of user choice accessed from the `growth_mediums_dict.py` file.
3. Uses the `single_gene_deletion()` function from COBRApy to knockdown each gene one at a time
4. Produces a report 


## Quick start
```
python single_gene_knockout_analysis.py --models -growth_media LB
```

## Dependancies
- cobra=0.20.0
- pandas=1.0.3
- python=3.6

## Installation
The best way to install this is to download this directory and run the script. Recommend to install within a conda environment.

```
# Create conda environment
conda create -y --name single_gene_knockout_analysis_env python=3.6.12

# Activate environment
conda activate single_gene_knockout_analysis_env

# Install dependancies
conda install -y -c bioconda cobra=0.20.0
pip install pandas==1.0.3

# Test script
python single_gene_knockout_analysis.py -h
```

## Usage
```
single_gene_knockout_analysis.py [-h] -m MODELS -g GROWTH_MEDIA [-y YA_NAME]

required arguments:
  -m MODELS, --models MODELS
                        Directory of model files to be annotated. Can be in .xml, .json or .sbml formats
  -g GROWTH_MEDIA, --growth_media GROWTH_MEDIA
                        Growth media in which models will be grown to test gene essentiality. Provided medias include: LB, M9, BG11, LB_CarveMe, nutrient_media, TSA, TSA_sheep_blood, PMM5_Mendoza,
                        PMM7_Mendoza, CDM_Mendoza

optional arguments:
  -y YA_NAME, --ya_name YA_NAME
                        What is ya name?
```

## Media options
Provided medias include:
- `LB`
- `M9`
- `BG11`
- `LB_CarveMe`
- `nutrient_media`
- `TSA`
- `TSA_sheep_blood`
- `PMM5_Mendoza`
- `PMM7_Mendoza`
- `CDM_Mendoza`

These are all using BiGG IDs. SEED IDs are on the way.
Look at the file format if you wish to create your own medias! Pretty easy to do!

## Authors

- Ben Vezina (https://scholar.google.com/citations?user=Rf9oh94AAAAJ&hl=en)
- Stephen C Watts (https://scholar.google.com/citations?user=lvS1IpkAAAAJ&hl=en)
