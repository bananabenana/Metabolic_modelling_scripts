VERSION = "1.0.0"

# Dependencies:
#   - cobra >=0.26.3
#   - pandas >=1.5.3
#   - python >=3.10.9

import argparse
import os
import glob
from cobra.io import validate_sbml_model, load_json_model, read_sbml_model
from pandas import DataFrame, read_csv, concat

def load_model(model_file):
    with open(model_file, 'r') as fh:
        if model_file.endswith('.sbml'):
            return validate_sbml_model(fh)
        elif model_file.endswith('.json'):
            return load_json_model(fh)
        elif model_file.endswith('.xml'):
            return read_sbml_model(fh)
        else:
            raise ValueError(f"Unsupported file format: {model_file}")

def generate_nodes(model):
    '''
    Generate node network file from model file

    '''
    nodes = [f"metabolite\tmetabolite_name\ttype\tmetabolite_compartment"]
    for m in model.metabolites:
        nodes.append(f"{m.id}\t{m.name}\tmetabolite\t{m.compartment}")
    return nodes

def generate_edges(model):
    '''
    Generate edge network file from model file

    '''
    edges = [f"reactant\tproduct\treaction_id\treaction_name\tinput_metabolite\tdirection\toutput_metabolite\tgenes\ttotal_redundant_genes"]
    for r in model.reactions:
        for m in r.reactants:
            for p in r.products:
                if r.gene_reaction_rule == "":
                    edges.append(f"{m.id}\t{p.id}\t{r.id}\t{r.name}\t{r.reaction}\tNONE\t0")
                else:
                    edges.append(f"{m.id}\t{p.id}\t{r.id}\t{r.name}\t{r.reaction}\t{r.gene_reaction_rule}\t{r.gene_reaction_rule.count('or')+1}")
    mapping = [ (' --> ', '\t -->\t'), (' <=> ', '\t<=>\t'), (' <-- ', '\t<--\t') ]
    for k, v in mapping:
        edges = [edge.replace(k, v) for edge in edges]
    return edges

def process_model_file(model_file, output_dir):
    '''
    Process model file

    '''
    print(f"Processing {model_file}...")
    model = load_model(model_file)
    nodes = generate_nodes(model)
    edges = generate_edges(model)

    model_name = os.path.splitext(os.path.basename(model_file))[0]
    nodes_output_file = os.path.join(output_dir, f"{model_name}_network_nodes.tsv")
    edges_output_file = os.path.join(output_dir, f"{model_name}_network_edges.tsv")

    with open(nodes_output_file, mode='w', encoding='utf-8') as out_nodes:
        out_nodes.write('\n'.join(nodes))

    with open(edges_output_file, mode='w', encoding='utf-8') as out_edges:
        out_edges.write('\n'.join(edges))

    print(f"Processed {model_file} and saved network files to {output_dir}")


def collate_reaction_ids(directory):
    '''
    Collate reaction IDs from *_network_edges.tsv files and produce a presence/absense matrix

    '''
    data = {}

    for file_path in glob.glob(os.path.join(directory, '*_network_edges.tsv')):
        model_name = os.path.splitext(os.path.basename(file_path))[0].replace('_network_edges', '')  # Remove '_network_edges' suffix
        edges_df = read_csv(file_path, sep='\t', usecols=['reaction_id'], dtype={'reaction_id': str})
        data[model_name] = edges_df['reaction_id'].tolist()

    unique_reaction_ids = sorted(set(reaction for reactions in data.values() for reaction in reactions))
    collation_matrix = DataFrame(index=unique_reaction_ids, columns=list(data.keys()))

    for model_name, reactions in data.items():
        collation_matrix[model_name] = collation_matrix.index.isin(reactions).astype(int)

    collation_matrix = collation_matrix.reset_index()
    collation_matrix.rename(columns={'index': 'reaction_id'}, inplace=True)

    return collation_matrix


def collate_metabolite_ids(directory):
    '''
    Collate metabolite IDs from *_network_nodes.tsv files and produce a presence/absense matrix

    '''
    data = {}

    for file_path in glob.glob(os.path.join(directory, '*_network_nodes.tsv')):
        model_name = os.path.splitext(os.path.basename(file_path))[0].replace('_network_nodes', '')  # Remove '_network_nodes' suffix
        nodes_df = read_csv(file_path, sep='\t', usecols=['metabolite'], dtype={'metabolite': str})
        data[model_name] = nodes_df['metabolite'].tolist()

    unique_metabolite_ids = sorted(set(metabolite for metabolites in data.values() for metabolite in metabolites))
    collation_matrix = DataFrame(index=unique_metabolite_ids, columns=list(data.keys()))

    for model_name, metabolites in data.items():
        collation_matrix[model_name] = collation_matrix.index.isin(metabolites).astype(int)

    collation_matrix = collation_matrix.reset_index()
    collation_matrix.rename(columns={'index': 'metabolite_id'}, inplace=True)

    return collation_matrix


def main():
    parser = argparse.ArgumentParser(description="Convert COBRA models to network files.")
    parser.add_argument("-d", "--directory", help="Path to the directory containing model files")
    parser.add_argument("-o", "--output", default="networks", help="Path to the output directory (default: networks)")
    parser.add_argument("-c", "--collate", help="Path to the directory containing network files to collate")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args()

    if args.collate and args.directory:
        print("Error: -c/--collate cannot be used with -d/--directory.")
        return

    # Collate reaction information if specified
    if args.collate:
        collation_matrix = collate_reaction_ids(args.collate)
        collation_matrix.to_csv(os.path.join(args.collate, 'reaction_presence_absence.tsv'), sep='\t', index=False)
        print("Collated reaction information saved as 'reaction_presence_absence.tsv'")

        # Collate metabolite information
        metabolites_collation_matrix = collate_metabolite_ids(args.collate)
        metabolites_collation_matrix.to_csv(os.path.join(args.collate, 'metabolite_presence_absence.tsv'), sep='\t', index=False)
        print("Collated metabolite information saved as 'metabolite_presence_absence.tsv'")

    if args.directory:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

        extensions = ['.xml', '.json', '.sbml']
        model_files = [file for ext in extensions for file in glob.glob(os.path.join(args.directory, '*' + ext))]

        for model_file in model_files:
            process_model_file(model_file, args.output)

        print("Enjoy your networks, or else")

if __name__ == "__main__":
    main()
