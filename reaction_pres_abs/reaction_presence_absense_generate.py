import os
import sys
from glob import glob
import pandas as pd
import cobra
from cobra.io import load_json_model, read_sbml_model
from argparse import ArgumentParser
from multiprocessing import Pool

def parse_arguments():
    parser = ArgumentParser(description='Create reaction presence and gene tables from metabolic models.')
    parser.add_argument('-m', '--master_model', help='Input master model file.')
    parser.add_argument('-d', '--directory', required=True, help='Input directory of metabolic models.')
    parser.add_argument('-o', '--output_prefix', required=True, help='Output name prefix.')
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads to use.')
    return parser.parse_args()

def read_model(file):
    if file.endswith('.json'):
        return load_json_model(file)
    elif file.endswith('.xml'):
        return read_sbml_model(file)

def process_model(file, master_model_rxns):
    model = read_model(file)
    model_rxns = [rxn.id for rxn in model.reactions]
    presence = [1 if rxn in model_rxns else 0 for rxn in master_model_rxns]
    print(f"{file} loaded and reactions determined")
    return presence, file

def get_grr_string(reaction):
    """Generate a gene-reaction rule (GRR) string for a reaction."""
    if reaction.gene_reaction_rule:
        return reaction.gene_reaction_rule.replace(" and ", ";").replace(" or ", ",")
    else:
        return ";".join([gene.id for gene in reaction.genes])

def main():
    args = parse_arguments()

    # Find all model files in the input directory
    json_files = glob(os.path.join(args.directory, '*.json'))
    xml_files = glob(os.path.join(args.directory, '*.xml'))
    model_files = json_files + xml_files
    print(f"Model file directory found with {len(model_files)} models")

    # Load the master model or generate it from all models in directory if not provided
    if args.master_model:
        # Load specified master model
        master_model = read_model(args.master_model)
        master_model_rxns = [rxn.id for rxn in master_model.reactions]
        master_model_genes = [(rxn.id, get_grr_string(rxn)) for rxn in master_model.reactions]
        print(f"{args.master_model} master model loaded with {len(master_model_rxns)} reactions.")
    else:
        # Generate master list from all models in directory
        all_rxns = set()
        all_genes = []
        for file in model_files:
            model = read_model(file)
            model_rxns = [rxn.id for rxn in model.reactions]
            all_rxns.update(model_rxns)
            all_genes.extend([(rxn.id, get_grr_string(rxn)) for rxn in model.reactions])
        master_model_rxns = sorted(all_rxns)
        master_model_genes = sorted(all_genes)
        print(f"Generated master reaction list from directory with {len(master_model_rxns)} reactions.")

    # Initialise results
    reaction_presence_matrix = pd.DataFrame(master_model_rxns, columns=['master_model_rxns'])
    gene_table = pd.DataFrame(master_model_genes, columns=['master_model_rxns', 'master_model_genes'])
    print(f"Master reaction and gene tables initialised")

    # Use multiprocessing to process models in parallel
    print(f"Processing models across {args.threads} threads")
    with Pool(args.threads) as pool:
        results = pool.starmap(process_model, [(file, master_model_rxns) for file in model_files])

    # Collect results
    print(f"Combining results from each model")
    presence_data = []
    for presence, file in results:
        model_name = os.path.splitext(os.path.basename(file))[0]
        presence_data.append(pd.Series(presence, name=model_name))

    # Concatenate all presence data into the reaction presence matrix
    presence_df = pd.concat(presence_data, axis=1)
    reaction_presence_matrix = pd.concat([reaction_presence_matrix, presence_df], axis=1)

    # Save the reaction presence table
    print(f"Writing {args.output_prefix}_reaction_presence_table.tsv")
    reaction_presence_table_path = f'{args.output_prefix}_reaction_presence_table.tsv'
    reaction_presence_matrix.to_csv(reaction_presence_table_path, sep='\t', index=False)

    # Save the reaction gene table
    print(f"Writing {args.output_prefix}_reaction_gene_table.tsv")
    reaction_gene_table_path = f'{args.output_prefix}_reaction_gene_table.tsv'
    gene_table.to_csv(reaction_gene_table_path, sep='\t', index=False)

if __name__ == '__main__':
    main()
