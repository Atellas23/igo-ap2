import pickle
import networkx as nx
from networkx.algorithms.clique import graph_number_of_cliques
import osmnx as ox
import csv
import urllib
from staticmap import StaticMap, Line, CircleMarker
import collections

Traffic_data = collections.namedtuple(
    'TData', ['id', 'name', 'coordinates', 'timestamp', 'state'])
Congestion = collections.namedtuple('Congestion', ['id', 'timestamp', 'state'])
Highway = collections.namedtuple('Highway', ['id', 'name', 'coordinates'])

CONGESTION_PONDERATIONS = {0: 1.75, 1: 1, 2: 1.25,
                           3: 1.5, 4: 2, 5: 3, 6: float('inf'), None: 1.75}


def exists_graph(graph_filename: str) -> bool:
    '''Checks if a certain graph file exists within the working directory.
    '''
    try:
        open(graph_filename, 'rb')
    except FileNotFoundError:
        return False
    return True


def load_graph(graph_filename):
    with open(graph_filename, 'rb') as file:
        graph = pickle.load(file)
    graph = nx.MultiDiGraph(incoming_graph_data=graph)
    return graph


def download_graph(place):
    graph = ox.graph_from_place(place, network_type='drive', simplify=True)
    # graph = ox.utils_graph.get_digraph(graph, weight='length')
    return graph


def save_graph(G, filename):
    G = nx.MultiDiGraph(incoming_graph_data=G)
    with open(filename, 'wb') as file:
        pickle.dump(G, file)


def plot_graph(G):
    fig, ax = ox.plot_graph(nx.MultiDiGraph(incoming_graph_data=G))
    fig.savefig('graph.png')


def download_highways(highways_url):
    highways = list()
    with urllib.request.urlopen(highways_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        for line in reader:
            way_id, description, coordinates = line
            coord = coordinates.split(',')
            highways.append(Highway(int(way_id), description,
                            [float(g) for g in coord]))
    return highways


def download_congestions(congestions_url):
    congestions = list()
    with urllib.request.urlopen(congestions_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')
        for line in reader:
            way_id, timestamp, current_state, _ = line
            congestions.append(Congestion(
                int(way_id), timestamp, int(current_state)))
    return congestions


def find_corresponding_congestion_data(highway, congestions):
    corresponding_congestion_data = None
    for cong in congestions:
        if cong.id == highway.id:
            corresponding_congestion_data = cong
            break
    return corresponding_congestion_data


def repack(highway, congestion):
    id, name, coordinates = highway
    _, datetime, current_state = congestion
    return Traffic_data(id, name, coordinates, datetime, current_state)


def build_complete_traffic_data(highways, congestions):
    complete_traffic_state_data = list()
    for highway in highways:
        congestion = find_corresponding_congestion_data(highway, congestions)
        repacked_data = repack(highway, congestion)
        complete_traffic_state_data.append(repacked_data)
    return complete_traffic_state_data


def plot_highways(highways, img_filename='highway_plot.png', size=800):
    m_bcn = StaticMap(size, size)
    for highway in highways:
        for i in range(0, len(highway.coordinates), 2):
            marker = CircleMarker(
                (highway.coordinates[i], highway.coordinates[i+1]), 'red', 3)
            m_bcn.add_marker(marker)
            if (i + 3 < len(highway.coordinates)):
                m_bcn.add_line(
                    Line(coords=(
                        (highway.coordinates[i], highway.coordinates[i+1]),
                        (highway.coordinates[i+2], highway.coordinates[i+3])),
                        color='blue', width=2))

    image = m_bcn.render()
    image.save(img_filename)


def color_decide(state):
    if state == 0:
        return 'grey'
    if state == 1:
        return '#00ff00'
    if state == 2:
        return '#aaff00'
    if state == 3:
        return '#ffe600'
    if state == 4:
        return '#ff8000'
    if state == 5:
        return '#ff1100'
    if state == 6 or state is None:
        return '#6042f5'


def plot_congestions(traffic_data, img_filename='congestion_plot.png',
                     size=800):
    m_bcn = StaticMap(size, size)
    for highway in traffic_data:
        for i in range(0, len(highway.coordinates), 2):
            marker = CircleMarker(
                (highway.coordinates[i], highway.coordinates[i+1]), 'black', 1)
            m_bcn.add_marker(marker)
            if (i + 3 < len(highway.coordinates)):
                m_bcn.add_line(
                    Line(coords=(
                        (highway.coordinates[i], highway.coordinates[i+1]),
                        (highway.coordinates[i+2], highway.coordinates[i+3])),
                        color=color_decide(highway.state), width=3))

    image = m_bcn.render()
    image.save(img_filename)


def _set_congestion(tdata: Traffic_data, graph):
    coord = tdata.coordinates
    edge_nodes_lat = list()
    edge_nodes_lng = list()
    # stupid_nodes = list()
    for i in range(0, len(coord), 2):
        edge_nodes_lat.append(coord[i])
        edge_nodes_lng.append(coord[i+1])
    nn = ox.nearest_nodes(graph, edge_nodes_lat, edge_nodes_lng)
    for i in range(1, len(nn)):
        orig = nn[i-1]
        dest = nn[i]
        try:
            path = ox.shortest_path(graph, orig, dest, weight='length')
        except Exception:
            # print(err)
            try:
                path = ox.shortest_path(graph, dest, orig, weight='length')
            except Exception as err2:
                print(err2)
                # print('no he trobat cap camí entre {a} i {b} :('.format(a=orig, b=dest))
                # stupid_nodes.append(orig)
                # stupid_nodes.append(dest)
                pass
        for i in range(1, len(path)):
            a = path[i-1]
            b = path[i]
            graph.adj[a][b][0]['congestion'] = tdata.state
    # return stupid_nodes
    return


def build_igraph(graph, traffic_data):
    nx.set_edge_attributes(graph, name='congestion', values=None)
    nx.set_edge_attributes(graph, name='itime', values=None)
    # ox.add_edge_bearings(graph)
    # stupid_nodes_2 = list()
    for data in traffic_data:
        _set_congestion(data, graph)
        # stupid_nodes_2.append(test)
    for _, info in graph.edges.items():
        try:
            speed = float(info['maxspeed'])/3.6
        except KeyError:
            speed = 30
        except TypeError:
            speed = sum(list(map(int, info['maxspeed'])))/len(info['maxspeed'])
        # base_itime =
        info['itime'] = (info['length']/speed) * \
            CONGESTION_PONDERATIONS[info['congestion']]
    # return stupid_nodes_2
    return


def build_ipath(igraph, origin, destiny):
    origin = origin + ', Barcelona'
    destiny = destiny + ', Barcelona'
    nn_origin = ox.nearest_nodes(
        igraph, ox.geocode(origin)[1], ox.geocode(origin)[0])
    nn_destiny = ox.nearest_nodes(
        igraph, ox.geocode(destiny)[1], ox.geocode(destiny)[0])

    return ox.shortest_path(igraph, nn_origin, nn_destiny, weight="itime")


def plot_path(igraph, ipath, img_filename='path_plot.png', size=800):
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
