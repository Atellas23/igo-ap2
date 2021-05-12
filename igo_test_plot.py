from time import sleep
import pickle
import networkx as nx
import osmnx as ox
import csv
import urllib
from functools import reduce
import pandas as pd
from staticmap import StaticMap, Line, CircleMarker

place = 'Barcelona, Catalonia'
graph_filename = 'barcelona.graph'
size = 800
highways_url = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
congestions_url = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'


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
            highways.append([int(way_id), description, [float(i) for i in coord]])
            # print(way_id, description, coordinates)
            # sleep(4)
    return highways


def download_congestions(congestions_url):
    congestions = list()
    with urllib.request.urlopen(congestions_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')
        for line in reader:
            way_id, timestamp, current_state, future_state = line
            congestions.append(
                [int(way_id), timestamp, int(current_state), int(future_state)])
            # way_id, description, coordinates = line
            # print(way_id, description, coordinates)
            # sleep(4)
    return congestions

def plot_highways(highways, img_filename, size):
    m_bcn = StaticMap(size, size)
    for row in highways:
        for i in range(0, len(row[2]), 2):
            marker = CircleMarker((row[2][i], row[2][i+1]), 'red', 3)
            m_bcn.add_marker(marker)
            if (i + 3 < len(row[2])):
                m_bcn.add_line(Line(((row[2][i], row[2][i+1]), (row[2][i+2], row[2][i+3])), 'blue', 2))

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

def plot_congestions(highways, congestions, img_filename, size):
    m_bcn = StaticMap(size, size)
    for row in highways:
        for i in range(0, len(row[2]), 2):
            marker = CircleMarker((row[2][i], row[2][i+1]), 'white', 4)
            m_bcn.add_marker(marker)
            if (i + 3 < len(row[2])):
                m_bcn.add_line(Line(((row[2][i], row[2][i+1]), (row[2][i+2], row[2][i+3])),
                                    0, 3))

    image = m_bcn.render()
    image.save(img_filename)

#color_decide(congestions[row[0]-1][2])
highways = download_highways(highways_url)
congestions = download_congestions(congestions_url)
plot_highways(highways, 'picture.png', 2000)
#plot_congestions(highways, congestions, 'picture.png',2000)    for row in highways:
