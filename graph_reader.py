import pickle
import osmnx
GRAPH_FILENAME = 'barcelona.graph'

with open(GRAPH_FILENAME, 'rb') as file:
    graph = pickle.load(file)

# for each node and its information...
for node1, info1 in graph.nodes.items():
    print(node1, info1)
    # for each adjacent node and its information...
    for node2, edge in graph.adj[node1].items():
        print('    ', node2)
        print('        ', edge)
