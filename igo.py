from re import template
from time import sleep
import pickle
import networkx as nx
import osmnx as ox
import csv
import urllib
from staticmap import StaticMap, Line, CircleMarker
import collections

Traffic_data = collections.namedtuple(
    'TData', ['id', 'name', 'coordinates', 'timestamp', 'state'])
Congestion = collections.namedtuple('Congestion', ['id', 'timestamp', 'state'])
Highway = collections.namedtuple('Highway', ['id', 'name', 'coordinates'])


def exists_graph(graph_filename):
    try:
        open(graph_filename, 'rb')
    except FileNotFoundError:
        return False
    return True


def load_graph(graph_filename):
    with open(graph_filename, 'rb') as file:
        graph = pickle.load(file)
    return graph


def download_graph(place):
    graph = ox.graph_from_place(place, network_type='drive', simplify=True)
    graph = ox.utils_graph.get_digraph(graph, weight='length')
    return graph


def save_graph(G, filename):
    with open(filename, 'wb') as file:
        pickle.dump(G, file)


def plot_graph(G):
    fig, ax = ox.plot_graph(nx.MultiDiGraph(incoming_graph_data=G))
    fig.savefig('temp_graph_img.png')


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


def plot_highways(highways, img_filename='temp_highways_plot.png', size=800):
    m_bcn = StaticMap(size, size)
    for highway in highways:
        for i in range(0, len(highway.coordinates), 2):
            marker = CircleMarker(
                (highway.coordinates[i], highway.coordinates[i+1]), 'red', 3)
            m_bcn.add_marker(marker)
            if (i + 3 < len(highway.coordinates)):
                m_bcn.add_line(
                    Line(((highway.coordinates[i], highway.coordinates[i+1]), (highway.coordinates[i+2], highway.coordinates[i+3])), 'blue', 2))

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


def plot_congestions(traffic_data, img_filename='temp_congestions_plot.png', size=800):
    m_bcn = StaticMap(size, size)
    for highway in traffic_data:
        for i in range(0, len(highway.coordinates), 2):
            marker = CircleMarker(
                (highway.coordinates[i], highway.coordinates[i+1]), 'black', 1)
            m_bcn.add_marker(marker)
            if (i + 3 < len(highway.coordinates)):
                m_bcn.add_line(Line(((highway.coordinates[i], highway.coordinates[i+1]), (highway.coordinates[i+2], highway.coordinates[i+3])),
                                    color_decide(highway.state), 3))

    image = m_bcn.render()
    image.save(img_filename)


def plot_path(igraph, ipath, img_filename, size):
    pass


def build_igraph(graph, highways, congestions):
    pass


def get_shortest_path_with_ispeeds(igraph, orig, dest):
    pass
