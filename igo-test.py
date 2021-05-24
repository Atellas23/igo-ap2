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
build_igraph(graph, complete_data)
path = build_ipath(graph, 'Zona Franca', 'Hospital de Sant Pau')
plot_path(graph, path)

# %%
path2 = build_ipath(graph, 'FME', 'Vallvidrera')
plot_path(graph, path2)

# %%


def _set_congestion(tdata: Traffic_data, graph):
    coord = tdata.coordinates
    l = len(coord)
    edge_nodes_lat = list()
    edge_nodes_lng = list()
    stupid_nodes = list()
    for i in range(0, l, 2):
        edge_nodes_lat.append(coord[i])
        edge_nodes_lng.append(coord[i+1])
    nn = ox.nearest_nodes(graph, edge_nodes_lat, edge_nodes_lng)
    for i in range(1, len(nn)):
        orig = nn[i-1]
        dest = nn[i]
        try:
            path = ox.shortest_path(graph, orig, dest, weight='length')
        except:
            try:
                path = ox.shortest_path(graph, dest, orig, weight='length')
            except:
                print(
                    'no he trobat cap camí entre {a} i {b} :('.format(a=orig, b=dest))
                stupid_nodes.append(orig)
                stupid_nodes.append(dest)
        for i in range(1, len(path)):
            a = path[i-1]
            b = path[i]
            graph.adj[a][b][0]['congestion'] = tdata.state
    return stupid_nodes


pond = {0: 1.75, 1: 1, 2: 1.25, 3: 1.5, 4: 2, 5: 3, 6: float('inf'), None: 1}


def build_igraph(graph, traffic_data):
    nx.set_edge_attributes(graph, name='congestion', values=None)
    nx.set_edge_attributes(graph, name='itime', values=None)
    # ox.add_edge_bearings(graph)
    stupid_nodes_2 = list()
    for data in traffic_data:
        test = _set_congestion(data, graph)
        stupid_nodes_2.append(test)
    for _, info in graph.edges.items():
        try:
            speed = float(info['maxspeed'])/3.6
        except KeyError:
            speed = 30
        except TypeError:
            speed = sum(list(map(int, info['maxspeed'])))/len(info['maxspeed'])
        # base_itime =
        info['itime'] = (info['length']/speed)*pond[info['congestion']]
    return stupid_nodes_2


# %%

def build_ipath(igraph, origin, destiny):
    origin = origin + ', Barcelona'
    destiny = destiny + ', Barcelona'
    nn_origin = ox.nearest_nodes(
        igraph, ox.geocode(origin)[1], ox.geocode(origin)[0])
    nn_destiny = ox.nearest_nodes(
        igraph, ox.geocode(destiny)[1], ox.geocode(destiny)[0])

    return ox.shortest_path(igraph, nn_origin, nn_destiny, weight="itime")


def plot_path(igraph, ipath, img_filename, size):
    m_bcn = StaticMap(size, size)
    try:
        origin_marker = CircleMarker((
            igraph.nodes[ipath[0]]['x'], igraph.nodes[ipath[0]]['y']), 'green', 9)
        destiny_marker = CircleMarker((
            igraph.nodes[ipath[-1]]['x'], igraph.nodes[ipath[-1]]['y']), 'green', 9)
        m_bcn.add_marker(origin_marker)
        m_bcn.add_marker(destiny_marker)

    except:
        print('There is no path')
    for i in range(0, len(ipath)):
        if (i + 1 < len(ipath)):
            line = Line(((igraph.nodes[ipath[i]]['x'], igraph.nodes[ipath[i]]['y']), (
                igraph.nodes[ipath[i+1]]['x'], igraph.nodes[ipath[i+1]]['y'])), '#0884ff', 3)
            m_bcn.add_line(line)

    image = m_bcn.render()
    image.save(img_filename)


# %%
non_nodes = build_igraph(graph, complete_data, _debug_nodes=True)
node_colors = list()
for node in graph.nodes:
    if node in non_nodes:
        node_colors.append('purple')
    else:
        node_colors.append('white')

edge_colors = list()
for edge, info in graph.edges.items():
    if info['congestion'] is not None:
        edge_colors.append(color_decide(info['congestion']))
    else:
        edge_colors.append('white')
ox.plot_graph(graph, figsize=(20, 20), node_size=3, node_color=node_colors,
              edge_color=edge_colors, save=True, filepath='tmp_tmp_tmp.png')


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
    ipath = build_ipath(
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
