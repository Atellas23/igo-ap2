# igo.py
'''iGo is a module to guide drivers through the streets of a city.

This module contains functions able to handle acquisition, storage and
consulting of graphs representing streets of a city, which must be kept
track of in OpenStreetMap (www.openstreetmap.org). The module also
relies on having the data of street congestion and geographic coordinates
accessible on the internet and in a particular format.

It was originally designed to do this with data from the city of Barcelona,
Catalonia, but can be (roughly) extended if one is keen on tinkering with
the module to work with other data formats.
'''

from collections import namedtuple
from typing import List, Optional, Union
from staticmap import StaticMap, Line, CircleMarker
from urllib import request
import csv
import osmnx as ox
import networkx as nx
import pickle

# We create the following types as named tuples from the collections
# standard module.
Highway = namedtuple(
    'Highway', ['id', 'name', 'coordinates'])
Congestion = namedtuple(
    'Congestion', ['id', 'timestamp', 'state'])

# We will be using the following named tuple as a base for the traffic
# data we collect from the internet.
Traffic_data = namedtuple(
    'Traffic_data', ['id', 'name', 'coordinates', 'timestamp', 'state'])

# And finally, these additional type definitions are used to make the
# code cleaner and easier to understand.
highway_list = List[Highway]
congestion_list = List[Congestion]
traffic_data_list = List[Traffic_data]

# This last one is used to annotate type even if we are not sure of what
# is going to come as a parameter, but are quite sure that will be one
# of the two types listed in the Union.
graph_type = Union[nx.MultiDiGraph, nx.DiGraph]


# The following constant is used to ponderate the time it takes to drive
# through a street depending on its congestion state.
CONGESTION_PONDERATIONS = {None: 1.75, 0: 1.75, 1: 1, 2: 1.25,
                           3: 1.5, 4: 2, 5: 3, 6: float('inf')}


def exists_graph(filename: str) -> bool:
    '''Checks if a certain graph file exists within the current working
    directory.
    '''
    try:
        open(filename, 'rb')
    except FileNotFoundError:
        return False
    return True


def load_graph(filename: str) -> nx.MultiDiGraph:
    '''Loads a certain file from the current working directory, assuming
    it exists. This can be checked with the 'exists_graph' function.
    '''
    with open(filename, 'rb') as file:
        graph = pickle.load(file)
    graph = nx.MultiDiGraph(incoming_graph_data=graph)
    return graph


def download_graph(place: str) -> nx.MultiDiGraph:
    '''Downloads the street graph from a physical place from the OSM
    database and returns it as a OSMnx graph object.
    '''
    graph = ox.graph_from_place(place, network_type='drive',
                                simplify=True)
    # graph = ox.utils_graph.get_digraph(graph, weight='length')
    return graph


def save_graph(G: graph_type, filename: str) -> None:
    '''Saves the received graph G as a file in the current working
    directory using the pickle library.
    '''
    G = nx.MultiDiGraph(incoming_graph_data=G)
    with open(filename, 'wb') as file:
        pickle.dump(G, file)


def plot_graph(G: graph_type, save: bool = False,
               filename: str = 'graph.png') -> None:
    '''Plots the received graph using the OSMnx plot function. Can save
    the image if needed through the arguments 'save' and 'filename'.
    '''
    fig, _ = ox.plot_graph(nx.MultiDiGraph(incoming_graph_data=G))
    if save:
        fig.savefig(filename)


def download_highways(highways_url: str) -> highway_list:
    '''Downloads the highway data from the received url.'''
    highways = list()
    with request.urlopen(highways_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        for line in reader:
            way_id, description, coordinates = line
            coord = coordinates.split(',')
            highways.append(Highway(int(way_id), description,
                            [float(g) for g in coord]))
    return highways


def download_congestions(congestions_url: str) -> congestion_list:
    '''Downloads the congestion data from the received url.'''
    congestions = list()
    with request.urlopen(congestions_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')
        for line in reader:
            way_id, timestamp, current_state, _ = line
            congestions.append(Congestion(
                int(way_id), timestamp, int(current_state)))
    return congestions


def find_corresponding_congestion_data(highway: Highway,
                                       congestions: congestion_list) \
        -> Congestion:
    '''Given a Highway and a list of Congestions, finds the congestion
    corresponding to the Highway data using their ID attributes.
    '''
    corresponding_congestion_data = None
    for cong in congestions:
        if cong.id == highway.id:
            corresponding_congestion_data = cong
            break
    return corresponding_congestion_data


def repack(highway: Highway, congestion: Congestion) -> Traffic_data:
    '''Utility function to convert a corresponding Highway, Congestion
    pair into a Traffic_data object.
    '''
    id, name, coordinates = highway
    _, datetime, current_state = congestion
    return Traffic_data(id, name, coordinates, datetime, current_state)


def build_complete_traffic_data(highways: highway_list,
                                congestions: congestion_list) \
        -> traffic_data_list:
    '''Constructs a list of Traffic_data elements given corresponding
    Highway and Congestion lists.
    '''
    complete_traffic_state_data = list()
    for highway in highways:
        congestion = find_corresponding_congestion_data(highway,
                                                        congestions)
        repacked_data = repack(highway, congestion)
        complete_traffic_state_data.append(repacked_data)
    return complete_traffic_state_data


def plot_highways(highways: highway_list,
                  filename: str = 'highway_plot.png',
                  size: int = 800) -> None:
    '''Plots the received Highway list into a map, giving the user
    insight about what streets exactly are documented in the internet
    data they downloaded. The plot is not shown but directly saved
    in a file, by default called 'highway_plot.png'.
    '''
    city_map = StaticMap(size, size)
    for highway in highways:
        for i in range(0, len(highway.coordinates), 2):
            marker = CircleMarker(
                (highway.coordinates[i], highway.coordinates[i+1]), 'red', 3)
            city_map.add_marker(marker)
            if (i + 3 < len(highway.coordinates)):
                city_map.add_line(
                    Line(coords=(
                        (highway.coordinates[i], highway.coordinates[i+1]),
                        (highway.coordinates[i+2], highway.coordinates[i+3])),
                        color='blue', width=2))

    image = city_map.render()
    image.save(filename)


def color_decide(state: int) -> str:
    '''Utility function to decide the corresponding color to a certain
    congestion state. Here is the color legend based on the congestions
    state:
    - If state is 'no information': grey
    - If state is 'very fluid traffic': green
    - If state is 'fluid traffic': greenish yellow
    - If state is 'dense traffic': yellow
    - If state is 'very dense traffic': orange
    - If state is 'congested traffic': red
    - If state is 'blocked street': navy blue
    '''
    if state == 0:
        return 'grey'
    if state == 1:
        return '#03fc2c'
    if state == 2:
        return '#c2fc03'
    if state == 3:
        return '#fc8f00'
    if state == 4:
        return '#ff8000'
    if state == 5:
        return '#fc0000'
    if state == 6 or state is None:
        return '#1c008a'


def plot_congestions(traffic_data: Traffic_data,
                     filename: str = 'congestion_plot.png',
                     size: int = 800) -> None:
    '''Plots the received Traffic_data list into a map, giving the user
    insight about what is the state of the streets that are kept track
    of in the available data. The plot is not shown but directly saved
    in a file, by default called 'congestion_plot.png'.
    '''
    city_map = StaticMap(size, size)
    for highway in traffic_data:
        for i in range(0, len(highway.coordinates), 2):
            marker = CircleMarker(
                (highway.coordinates[i], highway.coordinates[i+1]),
                'black', 1)
            city_map.add_marker(marker)
            if (i + 3 < len(highway.coordinates)):
                city_map.add_line(
                    Line(coords=(
                        (highway.coordinates[i], highway.coordinates[i+1]),
                        (highway.coordinates[i+2], highway.coordinates[i+3])),
                        color=color_decide(highway.state), width=3))

    image = city_map.render()
    image.save(filename)


def _set_congestion(tdata: Traffic_data, graph: nx.MultiDiGraph,
                    _debug_nodes: bool = False) -> Optional[list]:
    ''' Utility function that assings a congestion state to some of the edges in
    the OSMnx graph. For every highway from which we have congestion data we
    pick the end vertices and find the shortest path in the OSM graph, to every
    edge in the path we assign the congestion state of the highway. Can return a
    list of the nodes that could not be reached if needed through the argument
    '_debug_nodes'
    '''
    coord = tdata.coordinates
    edge_nodes_latitude = list()
    edge_nodes_longitude = list()
    if _debug_nodes:
        err_nodes = list()
    for i in range(0, len(coord), 2):
        edge_nodes_latitude.append(coord[i])
        edge_nodes_longitude.append(coord[i+1])
    nn = ox.nearest_nodes(graph, edge_nodes_latitude, edge_nodes_longitude)
    for i in range(1, len(nn)):
        origin = nn[i-1]
        destination = nn[i]
        try:
            path = ox.shortest_path(
                graph, origin, destination, weight='length')
            for i in range(1, len(path)):
                a = path[i-1]
                b = path[i]
                graph.adj[a][b][0]['congestion'] = tdata.state
        except nx.NetworkXNoPath:
            try:
                path = ox.shortest_path(
                    graph, destination, origin, weight='length')
                for i in range(1, len(path)):
                    a = path[i-1]
                    b = path[i]
                    graph.adj[a][b][0]['congestion'] = tdata.state
            except nx.NetworkXNoPath:
                if _debug_nodes:
                    print('No path has been found between nodes {} and {} in either direction.'.format(
                        origin, destination))
                    err_nodes.append(origin)
                    err_nodes.append(destination)
                pass
    if _debug_nodes:
        return err_nodes
    else:
        return


def build_igraph(graph: nx.MultiDiGraph, traffic_data: traffic_data_list,
                 _debug_nodes: bool = False) -> Optional[list]:
    ''' Utility function that adds the attributes 'congestion' and 'itime'
    to every edge in the OSM graph. itime is calculated dividing the edge
    length by the speed limit multiplied by a factor given by the edge
    congestion.
    '''
    nx.set_edge_attributes(graph, name='congestion', values=None)
    nx.set_edge_attributes(graph, name='itime', values=None)
    err_nodes = list()
    for data in traffic_data:
        failed_nodes = _set_congestion(data, graph, _debug_nodes)
        if _debug_nodes:
            for node in failed_nodes:
                err_nodes.append(node)
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
    if _debug_nodes:
        return err_nodes
    else:
        return


def build_ipath(igraph: nx.MultiDiGraph, origin: str, destiny: str) -> list:
    ''' Returns the shortest path between two locations in the city of Barcelona
    given by their names (street, building name, etc.)
    '''
    origin = origin + ', Barcelona'
    destiny = destiny + ', Barcelona'
    nn_origin = ox.nearest_nodes(
        igraph, ox.geocode(origin)[1], ox.geocode(origin)[0])
    nn_destiny = ox.nearest_nodes(
        igraph, ox.geocode(destiny)[1], ox.geocode(destiny)[0])

    return ox.shortest_path(igraph, nn_origin, nn_destiny, weight="itime")


def plot_path(igraph: nx.MultiDiGraph, ipath: list,
              filename: str = 'path_plot.png',
              size: int = 800) -> None:
    ''' Plots the received shortest_path list into a map. The plot is not
    shown but directly saved in a file, by default called 'path_plot.png'.
    '''
    city_map = StaticMap(size, size)
    try:
        origin_marker = CircleMarker((
            igraph.nodes[ipath[0]]['x'], igraph.nodes[ipath[0]]['y']), 'green', 9)
        destiny_marker = CircleMarker((
            igraph.nodes[ipath[-1]]['x'], igraph.nodes[ipath[-1]]['y']), 'green', 9)
        city_map.add_marker(origin_marker)
        city_map.add_marker(destiny_marker)

    except:
        print('There is no path')
    for i in range(0, len(ipath)):
        if (i + 1 < len(ipath)):
            line = Line(((igraph.nodes[ipath[i]]['x'], igraph.nodes[ipath[i]]['y']), (
                igraph.nodes[ipath[i+1]]['x'], igraph.nodes[ipath[i+1]]['y'])), '#0884ff', 3)
            city_map.add_line(line)

    image = city_map.render()
    image.save(filename)
