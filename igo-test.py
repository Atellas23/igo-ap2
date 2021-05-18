# %%
from time import sleep
from igo import *
PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

# %%
graph = load_graph(GRAPH_FILENAME)
highways = download_highways(HIGHWAYS_URL)
congestions = download_congestions(CONGESTIONS_URL)
complete_data = build_complete_traffic_data(highways, congestions)
plot_graph(graph)
plot_highways(highways)
plot_congestions(complete_data)


# %%
def map_data_to_graph(data, graph: nx.MultiDiGraph):
    # for dd in data:
    dd = data[int(len(data)/2)]
    print('estem al carrer', dd.name, sep=' ')
    coord = dd.coordinates
    l = len(coord)
    print('    passa pels següents nodes:')
    edge_nodes_lat = list()
    edge_nodes_lng = list()
    for i in range(0, l, 2):
        edge_nodes_lat.append(coord[i])
        edge_nodes_lng.append(coord[i+1])
        # c1 = coord[i]
        # c2 = coord[i+1]
    nn = ox.nearest_nodes(graph, edge_nodes_lat, edge_nodes_lng)
    node_colors = [
        'red' if node in nn else 'white' for node in graph.nodes]
    print(node_colors.index('red'))
    for node in nn:
        print('     -->', node)
    ox.plot_graph(graph, node_color=node_colors, node_size=3, figsize=(800,800))
    return

# %%


def test():
    # load/download graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME):
        print('File does not exist, downloading.')
        graph = download_graph(PLACE)
        save_graph(graph, GRAPH_FILENAME)
    else:
        print('File exists!')
        graph = load_graph(GRAPH_FILENAME)
    plot_graph(graph)

    # download highways and plot them into a PNG image
    highways = download_highways(HIGHWAYS_URL)
    plot_highways(highways, 'highways.png', SIZE)

    # download congestions and plot them into a PNG image
    congestions = download_congestions(CONGESTIONS_URL)
    complete_data = build_complete_traffic_data(highways, congestions)
    plot_congestions(complete_data, 'congestions.png', SIZE)

    # get the 'intelligent graph' version of a graph taking into account the congestions of the highways
    igraph = build_igraph(graph, complete_data)

    # get 'intelligent path' between two addresses and plot it into a PNG image
    ipath = get_shortest_path_with_ispeeds(
        igraph, "Campus Nord", "Sagrada Família")
    plot_path(igraph, ipath, 'ipath.png', SIZE)


test()

# # for each node and its information...
# for node1, info1 in graph.nodes.items():
#     print(node1, info1)
#     # for each adjacent node and its information...
#     for node2, edge in graph.adj[node1].items():
#         print('    ', node2)
#         print('        ', edge)


'''
for node, info in graph.nodes.items():
    print('cruilla a:', node, sep=' ')
    print('te info:', info, sep=' ')
    for neighbour, info2 in graph.adj[node].items():
        print('te vei:', node, sep=' ')
        print('els connecta el carrer:',info2,sep=' ')
        sleep(10)
    print(10*'-')
'''
