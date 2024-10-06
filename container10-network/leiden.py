import networkx as nx
import pandas as pd
import igraph as ig
import leidenalg as la
import numpy as np

data_folder = '/hpf/largeprojects/pmaass/Milad/Community_detection/AWS'
data = pd.read_csv(f'{data_folder}/cd_format.10000.txt', delimiter=r'\s+', engine='python')
#data = pd.read_csv(f'{data_folder}/cd_format.10000.txt', delimiter='\t', nrows=5)

print(data.head())
print(data.columns)

# Manually rename columns to ensure they match your expectations
#data = pd.read_csv(f'{data_folder}/cd_format.10000.txt', delimiter='\t')

data.columns = ['chrA_ID', 'chrB_ID', 'freq']


#data = pd.read_csv(
#    f'{data_folder}/cd_format.10000.txt',
#    usecols=['chrA_ID', 'chrB_ID', 'freq'],
#    delimiter='\t'
#)

# Adjust weights to be non-negative
min_weight = data['freq'].min()
data['freq'] = data['freq'] + abs(min_weight)

# Create the graph from the edgelist
graph = nx.from_pandas_edgelist(data, source='chrA_ID', target='chrB_ID', edge_attr='freq')

print(f'Number of nodes: {nx.number_of_nodes(graph)}')
print(f'Number of edges: {nx.number_of_edges(graph)}')

# Determine the weight threshold for the weakest 20% of edges
#sorted_weights = sorted(nx.get_edge_attributes(graph, 'freq').values())
#threshold_index = int(len(sorted_weights) * 0.2)
#weight_threshold = sorted_weights[threshold_index]

# Remove edges with weight below the threshold
#edges_to_remove = [(u, v) for u, v, w in graph.edges(data=True) if w['freq'] < weight_threshold]
#graph.remove_edges_from(edges_to_remove)

#print(f'Number of nodes after pruning: {nx.number_of_nodes(graph)}')
#print(f'Number of edges after pruning: {nx.number_of_edges(graph)}')

# Convert NetworkX graph to igraph
edges = [(u, v, float(w['freq'])) for u, v, w in graph.edges(data=True)]
igraph_graph = ig.Graph.TupleList(edges, directed=False, edge_attrs=['freq'])

# Apply Leiden algorithm for community detection
#partitions = leidenalg.find_partition(igraph_graph, leidenalg.ModularityVertexPartition, weights='freq')
#partitions = la.find_partition(igraph_graph, la.ModularityVertexPartition, weights='freq', resolution_parameter=2)

#resolution_value = 2.0  # Adjust this value as needed to increase the number of communities

#partition_type = la.ModularityVertexPartition(igraph_graph, weights='freq', resolution_parameter=resolution_value)
#partitions = la.find_partition(igraph_graph, resolution_value, weights='freq')

#################
#n_comms = 46
#partition = la.CPMVertexPartition(igraph_graph, 
#                                  initial_membership=np.random.choice(n_comms, 100),
#                                  resolution_parameter=2)

#resolution_value = 2.0  # Adjust this value as needed to increase the number of communities

#partition_type = la.ModularityVertexPartition(igraph_graph, weights='freq', resolution_parameter=resolution_value)
#partitions = la.find_partition(igraph_graph, partition_type)

# Run Leiden algorithm with a specified number of iterations
#n_iterations = 100  # Increase or decrease this value to find more or fewer communities

#partition_type = la.ModularityVertexPartition(igraph_graph, weights='freq')
#partitions = la.find_partition(igraph_graph, partition_type, n_iterations=n_iterations)

# Check the number of communities
#print(f"Number of communities: {len(partitions)}")

resolution_value = 1.8  # Adjust this value to control the number of communities

partitions = la.find_partition(igraph_graph, la.RBConfigurationVertexPartition, weights='freq', resolution_parameter=resolution_value)

# Check the number of communities
print(f"Number of communities: {len(partitions)}")


# Prepare the results
comms = {}
for node in range(len(partitions.membership)):
    community = partitions.membership[node]
    if community not in comms:
        comms[community] = [igraph_graph.vs[node]['name']]
    else:
        comms[community].append(igraph_graph.vs[node]['name'])

print(f'Number of communities: {len(comms)}')

# Save each node and its community ID to a file
with open(f'{data_folder}/test_10KB_full.txt', 'w') as file:
    # create a list to store the rows of the dataframe
    rows = []
    # initialize the community ID counter to 1
    com_id = 1
    # iterate over each element in the list
    for com, nodes in comms.items():
        # iterate over each node in the community
        for node in nodes:
            # append a row to the list with the node ID and community ID
            rows.append([node, com_id])
        # increment the community ID counter for the next community
        com_id += 1
    # create a dataframe from the rows list
    df = pd.DataFrame(rows, columns=['ID name', 'Community ID'])
    # write the dataframe to the file as a CSV
    df.to_csv(file, index=False)

