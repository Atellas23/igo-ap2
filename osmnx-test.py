# %%
import networkx as nx
import pickle
import osmnx as ox
PLACE = 'Barcelona, Catalonia'
graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
ox.plot_graph(graph)

# %%
with open('barcelona.graph', 'wb') as file:
    pickle.dump(graph, file)
# %%
FILENAME = 'barcelona.graph'
try:
    with open(FILENAME, 'rb') as file:
        test_object = pickle.load(file)
except FileNotFoundError:
    print("File", FILENAME, "does not exist", sep=' ')
# %%
ox.plot_graph(test_object)
# %%

FILENAME = 'barcelona.graph'


def exists_graph(GRAPH_FILENAME):
    try:
        open(GRAPH_FILENAME, 'rb')
    except FileNotFoundError:
        return False
    return True


def load_graph(GRAPH_FILENAME):
    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pickle.load(file)
    return graph


if exists_graph(FILENAME):
    graph = load_graph(FILENAME)
    ox.plot_graph(graph)
else:
    print('file', FILENAME, 'does not exist', sep=' ')
# %%


def download_graph(PLACE):
    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    graph = ox.utils_graph.get_digraph(graph, weight='length')
    return graph


def save_graph(G, FILENAME):
    with open(FILENAME, 'wb') as file:
        pickle.dump(G, file)


def plot_graph(G):
    ox.plot_graph(G)


# %%
test_g = nx.MultiDiGraph(incoming_graph_data=g)
ox.plot_graph(test_g)
# %%


def plot_graph(G):
    ox.plot_graph(nx.MultiDiGraph(incoming_graph_data=G))
# %%
