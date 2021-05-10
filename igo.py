from time import sleep
import pickle
import networkx as nx
import osmnx as ox
import csv
import urllib
from functools import reduce


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
            highways.append([int(way_id), description, coordinates])
            # print(way_id, description, coordinates)
            # sleep(4)
    return highways


def download_congestions(congestions_url):
    congestions = list()
    with urllib.request.urlopen(congestions_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        for line in reader:
            congestions.append(line)
            # way_id, description, coordinates = line
            # print(way_id, description, coordinates)
            # sleep(4)
    return congestions


def plot_highways(highways, img_filename, size):
    pass


def plot_congestions(highways, congestions, img_filename, size):
    pass


def plot_path(igraph, ipath, img_filename, size):
    pass


def build_igraph(graph, highways, congestions):
    pass


def get_shortest_path_with_ispeeds(igraph, orig, dest):
    pass
