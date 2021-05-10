import pickle
import osmnx
PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'

graph = osmnx.graph_from_place(PLACE, network_type='drive', simplify=True)
graph = osmnx.utils_graph.get_digraph(graph, weight='length')

with open(GRAPH_FILENAME, 'wb') as file:
    pickle.dump(graph, file)
