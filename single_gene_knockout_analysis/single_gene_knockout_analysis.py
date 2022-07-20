##### Single gene knockout/deletion analysis on COBRA metabolic models to study gene essentiality

"""
This script runs a user-friendly version of single_gene_deletion() function from COBRApy. Each gene within a metabolic model will be iteratively deleted one by one, then growth tested on either a supplied or custom in silico growth media. If model growth (biomass) is above ≥ 0.0001, growth has taken place and the resulting gene is NOT essential in that growth media environment. This allows the user to get an overview of which genes are essential or non-essential.
User can provide input model files in any format (.xml, .json or .sbml).
"""

### Authors
"""
Ben Vezina (https://scholar.google.com/citations?user=Rf9oh94AAAAJ&hl=en)
Stephen C Watts (https://scholar.google.com/citations?user=lvS1IpkAAAAJ&hl=en)
"""

### Dependancies
"""
cobra=0.20.0
pandas=1.0.3
"""

### Import packages
import cobra
from cobra.io import read_sbml_model, load_model, load_json_model, validate_sbml_model
from cobra.flux_analysis import single_gene_deletion
import os
from glob import glob
import argparse
import json
import sys
import pandas as pd
from growth_mediums_dict import growth_mediums as media

### Define user input arguments
parser = argparse.ArgumentParser(description = 'Help for single_gene_knockout_analysis.py')
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
required.add_argument('-m', '--models', help = 'Directory of model files to be annotated. Can be in .xml, .json or .sbml formats', required = True) # args.models
required.add_argument('-g', '--growth_media', help = 'Growth media in which models will be grown to test gene essentiality. Provided medias include: LB, M9, BG11, LB_CarveMe, nutrient_media, TSA, TSA_sheep_blood, PMM5_Mendoza, PMM7_Mendoza, CDM_Mendoza', required = True) # args.growth_media
optional.add_argument('-y', '--ya_name', help = 'What is ya name?') # args.ya_name
args = parser.parse_args()
# args = parser.parse_args('-m models -g LB_CarveMe'.split())

### Define functions

# Define function for initialising model in a growth media prior to running single gene knockout
def media_environment_function(model, growth_media_choice):
    for reaction in model.reactions:
        if 'EX_' in  reaction.id:
            reaction.lower_bound=0
    # for reaction_id, lower_bound in media.M9.items():
    for reaction_id, lower_bound in media[growth_media_choice].items():
        try:
            reaction = model.reactions.get_by_id(reaction_id)
        except KeyError:
            msg = f'Model does not contain reaction {reaction_id} and was not modified'
            print(msg, file=sys.stderr)
        reaction.lower_bound = lower_bound
        print("Modified " + str(reaction_id) + "in " + str(model) + ".")


### Run script

# Say hello
if args.ya_name is None:
    print("Hi stranger, lets run some single gene knockouts")
else:
    print("Hi " + str(args.ya_name) + ", lets run some single gene knockouts")

# Create directories
directory_list = ('Single_gene_deletions', 'logs')
for directory in directory_list:
    try:
        os.mkdir(directory)
    except OSError:
        print ("Creation of the directory %s failed" % directory)
    else:
        print ("Successfully created the directory %s " % directory)

# Read models in any format (.xml, .json, .sbml)
files = glob(str(args.models) + '/*.json') + glob(str(args.models) + '/*.xml') + glob(str(args.models) + '/*.sbml') # files = glob('models/*.json') + glob('models/*.xml') + glob('models/*.sbml')

# Run single gene deletion and loop through all models
for model_file in files:
    # read sbml format
    if model_file.endswith('.sbml'):
        model, errors = validate_sbml_model(model_file) # doesn't print annoying errors due to legacy format...
    # read json format
    elif model_file.endswith('.json'):
    # if model_file.suffix == '.json': # use this for string-based method
        model = load_json_model(model_file)
    elif model_file.endswith('.xml'):
        model = read_sbml_model(model_file)
    media_environment_function(model, args.growth_media)
    results = single_gene_deletion(model)
    results_str_replace = results.replace('{', "").replace('}', "").replace('\'', "") # modify file to remove weird dict stuff
	# Write to file
    results_str_replace.to_csv('Single_gene_deletions/' + str(model) + '_on_' + str(args.growth_media) + '_single_gene_deletions.tsv', sep='\t', index = False)
    print('Single gene deletion for ' + str(model) + ' on ' + str(args.growth_media) + ' media computed')
