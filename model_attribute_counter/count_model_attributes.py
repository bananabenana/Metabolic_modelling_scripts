import os
import argparse
import pandas as pd
from multiprocessing import Pool, cpu_count, Manager
from cobra.io import read_sbml_model, load_json_model

def count_model_components(model):
    num_reactions = len(model.reactions)
    num_genes = len(model.genes)
    num_metabolites = len(model.metabolites)
    return num_reactions, num_metabolites, num_genes

def count_reactions_metabolites_genes(model_path):
    # Determine file type based on extension
    file_extension = os.path.splitext(model_path)[1]

    if file_extension == ".xml":
        # Load SBML model
        model = read_sbml_model(model_path)
    elif file_extension == ".json":
        # Load JSON model
        model = load_json_model(model_path)
    else:
        raise ValueError("Unsupported file format. Supported formats: .xml (SBML) and .json")

    # Get the number of reactions, metabolites, and genes
    num_reactions, num_metabolites, num_genes = count_model_components(model)
    
    return num_reactions, num_genes, num_metabolites

def process_models(directory_path, num_processes):
    print(f'Scanning directory {directory_path} for models...')
    filenames = [f for f in os.listdir(directory_path) if f.endswith(".xml") or f.endswith(".json")]
    total_files = len(filenames)
    print(f'Found {total_files} model files')

    print(f'Processing models with {num_processes} processes...')
    
    # Create a multiprocessing Manager to share variables
    manager = Manager()
    processed_counter = manager.Value('i', 0)
    
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_model, [(filename, directory_path, total_files, processed_counter) for filename in filenames])
    
    # Filter out any None results
    results = [result for result in results if result is not None]

    # Create the DataFrame from the list of results
    df = pd.DataFrame(results, columns=['Model', 'Num_reactions', 'Num_genes', 'Num_metabolites'])
    
    print('Finished processing all models')
    return df

def process_model(args):
    filename, directory_path, total_files, processed_counter = args
    if filename.endswith(".xml") or filename.endswith(".json"):
        model_path = os.path.join(directory_path, filename)

        # Extract model name from the filename
        model_name = os.path.splitext(filename)[0]

        # Count reactions, metabolites, and genes
        num_reactions, num_genes, num_metabolites = count_reactions_metabolites_genes(model_path)
        
        # Increment the counter
        processed_counter.value += 1

        # Calculate progress percentage with two decimal places
        progress = round(processed_counter.value / total_files * 100, 2)

        print(f'{progress}% of models processed. Model: {model_name}, Reactions: {num_reactions}, Genes: {num_genes}, Metabolites: {num_metabolites}')
        return {'Model': model_name, 'Num_reactions': num_reactions, 'Num_genes': num_genes, 'Num_metabolites': num_metabolites}

    return None

def main():
    parser = argparse.ArgumentParser(description='Count reactions, metabolites, and genes in COBRA models.')
    parser.add_argument('-d', '--directory', required=True, help='Path to the directory containing .xml or .json COBRA models')
    parser.add_argument('-o', '--output', default='output.tsv', help='Output filename (default: output.tsv)')
    parser.add_argument('-p', '--processes', type=int, default=cpu_count(), help='Number of processes for parallel processing (default: number of CPU cores)')

    args = parser.parse_args()
    models_directory = args.directory
    output_filename = args.output
    num_processes = args.processes

    print(f'Starting processing of models in {models_directory} with {num_processes} processes...')

    # Process models and create the DataFrame
    result_df = process_models(models_directory, num_processes)

    # Save the DataFrame as a TSV file
    result_df.to_csv(output_filename, sep='\t', index=False)
    print(f'Results saved to {output_filename}')

if __name__ == "__main__":
    main()
