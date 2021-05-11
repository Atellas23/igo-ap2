# %%
from time import sleep
from igo import *
import collections
PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

# Highway = collections.namedtuple('Highway', '...')  # Tram
# Congestion = collections.namedtuple('Congestion', '...')

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
    plot_congestions(highways, congestions, 'congestions.png', SIZE)

    # get the 'intelligent graph' version of a graph taking into account the congestions of the highways
    igraph = build_igraph(graph, highways, congestions)

    # get 'intelligent path' between two addresses and plot it into a PNG image
    ipath = get_shortest_path_with_ispeeds(
        igraph, "Campus Nord", "Sagrada Família")
    plot_path(igraph, ipath, 'ipath.png', SIZE)


# %%
test()
# %%
highways = download_highways(HIGHWAYS_URL)
congestions = download_congestions(CONGESTIONS_URL)
graph = load_graph(GRAPH_FILENAME)
print(len(highways))
print(len(congestions))
# %%
# for each node and its information...
for node1, info1 in graph.nodes.items():
    print(node1, info1)
    # for each adjacent node and its information...
    for node2, edge in graph.adj[node1].items():
        print('    ', node2)
        print('        ', edge)
    sleep(5)
# %%
complete_traffic_state_data = list()
n = len(highways)
highway = highways[int(n/2)]


def find_corresponding_congestion_data(highway):
    corresponding_congestion_data = None
    for cong in congestions:
        if cong[0] == highway[0]:
            corresponding_congestion_data = cong
            break
    return corresponding_congestion_data


congest = find_corresponding_congestion_data(highway)
id, name, orig_lat, orig_lng, dest_lat, dest_lng = highway
_, datetime, current_state, _ = congest
complete_traffic_state_data.append(
    [id, name, orig_lat, orig_lng, dest_lat, dest_lng, datetime, current_state])


# %%
def repack(highway, congestion):
    id, name, orig_lat, orig_lng, dest_lat, dest_lng = highway
    _, datetime, current_state, _ = congestion
    return [id, name, orig_lat, orig_lng, dest_lat, dest_lng, datetime, current_state]


def build_complete_traffic_data(highways, congestions):
    complete_traffic_state_data = list()
    for highway in highways:
        congestion = find_corresponding_congestion_data(highway)
        repacked_data = repack(highway, congestion)
        complete_traffic_state_data.append(repacked_data)
    return complete_traffic_state_data
# %%
