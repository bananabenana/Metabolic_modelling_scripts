# Converting metabolic models to network files

This is a script which converts COBRA models [.json, .xml, .sbml] to network files of reactions as edges and metabolites as nodes. 
These can also be collated into a presence/absense matrix.

The application of this is to construct large volumes of metabolic models then leverage these for comparative population metabolism analysis. Models can be
constructed using our tool [Bactabolize](https://github.com/kelwyres/Bactabolize), or the wonderful [CarveMe](https://github.com/cdanielmachado/carveme), then
networks can be constructed and analysed en masse.

## Usage
This script has two main functions. The first is to construct networks and second is to collate networks

To construct networks from a directory containing metabolic model files:
```
python3 model_to_network.py -d model_directory -o networks_dir
```
Outputs:
| File  	|  Description 	| Use  	|
|---	|---	|---	|
| *_network_nodes.tsv  	|  Network node file containing 4 columns, with metabolite_id as column 1 used as the node, followed by metabolite characteristics for extended analysis and visualisation  |  Used as input for igraph 	| 
| *_network_edges.tsv  	|  Network edge file containg 9 columns, with reactant metabolite in column 1, product of reaction in column 2, reaction_id in column 3, followed by metadata of reaction for extended analysis and visualisation. Column 9 contains the total amount of genes encoding this reaction as 'OR' statements, to give an indication of gene redundancy within the metabolic network. This is useful to visualise as edge weight for example   	|  Used as input for igraph 	|  


To collate networks into a presence/absense table of reactions and metabolites
```
python3 model_to_network.py -c networks_dir
```
Outputs:
| File  	|  Description 	| Use  	|
|---	|---	|---	|
| metabolite_presence_absence.tsv  	|  Binary presence/absense table showing the presence of each metabolite (rows) along each network (columns)   |  Used as input for many things including heatmaps, co-occurrence analysis, machine learning, GWAS etc 	| 
| reaction_presence_absence.tsv  	| Binary presence/absense table showing the presence of each reaction (rows) along each network (columns)    |  Used as input for many things including heatmaps, co-occurrence analysis, machine learning, GWAS etc 	|  


## Downstream analysis
The *_network_nodes.tsv and *_network_edges.tsv files can be used as input for igraph (in R) as follows:
```
library(igraph)
# Load edges file
edges <- read.delim('model_network_edges.tsv', na.strings = c("NONE"))

# Load nodes file
nodes <- read.delim('model_network_nodes.tsv')

# Construct graph using igraph
g <- graph_from_data_frame(edges, directed=TRUE, vertices = nodes)

# Plot with base R
plot(g)
```
This can be further beautified using ggraph or ggnetwork etc, but outside the scope of this readme.
The below figure was done usign ggraph
![metabolic_network_graph_graphopt4](https://github.com/bananabenana/Metabolic_modelling_scripts/assets/19924405/da5b0950-59f9-4b9d-9eb0-5f5795d77b12)

## Dependencies
- cobra >=0.26.3
- pandas >=1.5.3
- python >=3.10.9

## Author
Ben Vezina
- ORCID: 0000-0003-4224-2537
- https://scholar.google.com/citations?user=Rf9oh94AAAAJ&hl=en&oi=ao


## Citation

Please reference this github page, zenodo coming soon
