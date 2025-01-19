# Generate reaction presence/absense table

This multi-threaded script generates a reaction presence/absense table for a directory containing metabolic models.

## Quick usage
```bash
# Run on directory of metabolic models using 16 threads
python reaction_presence_absense_generate.py \
  -m ref_model/iML1515.json \
  -d bactabolize_models \
  -o bactabolize_models_rxn \
  -t 16
```

## Options

`--master_model`/`-m`: Input master model file which should contain all possible reactions. Can be either a pan model or universal model

`--directory`/`-d`: Input directory containing metabolic models

`--output_prefix`/`-o`: Output name prefix

`--threads`/`-t`: Number of threads to use. The more, the better, as genes and reactions are calculated individually on a per-model basis


## Requirements

- pandas
- cobrapy

## Authors

- Ben Vezina (https://scholar.google.com/citations?user=Rf9oh94AAAAJ&hl=en)



