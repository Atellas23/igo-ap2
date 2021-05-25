# importa l'API de Telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import igo
import os
from datetime import date, datetime, timedelta
from urllib import request
import xml.etree.ElementTree as ET

# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

graph = igo.load_graph(GRAPH_FILENAME)
highways = igo.download_highways(HIGHWAYS_URL)
congestions = igo.download_congestions(CONGESTIONS_URL)
complete_data = igo.build_complete_traffic_data(highways, congestions)
igo.build_igraph(graph, complete_data)


def get_last_known_time(traffic_data: igo.Traffic_data):
    time = datetime.strptime(traffic_data.timestamp, '%Y%m%d%H%M%S')
    return time


def time_to_update(traffic_data: igo.Traffic_data):
    last_known_time = get_last_known_time(traffic_data)
    if last_known_time-datetime.now() >= timedelta(minutes=5):
        return True
    else:
        return False


def update_data(dataset: igo.traffic_data_list):
    congestions = igo.download_congestions(CONGESTIONS_URL)
    dataset.clear()
    dataset = igo.build_complete_traffic_data(highways, congestions)


def get_location_name(lat, lon):
    base_url = 'https://nominatim.openstreetmap.org/reverse?\
lat={lat}&lon={lon}'
    response = request.urlopen(base_url.format(lat=lat, lon=lon))
    lines = [l.decode('utf-8') for l in response.readlines()]
    result = ''.join(lines)
    root = ET.fromstring(result)
    return root[0].text


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Welcome to IGO, the newest navigation \
tool to travel at light speed through Barcelona.')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='If you want to use IGO, you will have \
to send me your current location using the Location sharing option from \
Telegram itself.')


def help(update, context):
    HELP_MSG = '''My commands are:
    - /start: Starts the conversation with IGO.
    - /author: Returns information from the project authors.
    - /go: Requires a location from the city of Barcelona and returns
    the shortest path from the user's current location.
    - /where: Returns the users current location. This can only be called
    once a location has been set. If it has not been set, an message will
    appear asking you to send your location.
    '''
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=HELP_MSG)


def author(update, context):
    AUTHORS_MSG = '''This project's authors are:
    Àlex Batlle Casellas, Arenys de Munt, 2001.
    Pere Cornellà Franch, Fornells de la Selva, 2002.
    '''
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=AUTHORS_MSG)


def go(update, context):
    if time_to_update(complete_data[0]):
        update_data()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='iGo calculated the following minimal \
path taking into account public congestion data.')
    destination = str(context.arguments[0])
    path = igo.build_ipath(
        graph, context.user_data['current_position'], destination)
    filename = 'path_'+update.effective_chat.username+'.png'
    igo.plot_path(graph, path, filename=filename)
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(filename, 'rb'))
    os.remove(filename)


def where(update, context):
    try:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        context.user_data['current_position'] = get_location_name(lat, lon)
        context.user_data['current_coordinates'] = {'lat': lat, 'lon': lon}
        filename = 'position_' + update.effective_chat.username + '.png'
        map = igo.StaticMap(500, 500)
        map.add_marker(igo.CircleMarker((lon, lat), 'blue', 10))
        image = map.render()
        image.save(filename)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(filename, 'rb'))
        os.remove(filename)
    except Exception as e:
        # print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣: something went wrong while checking your current \
position')


def say_where(update, context):
    WHERE_MSG = 'You are currently at '
    if 'current_position' not in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please send your location \
before asking for your position.')
        return
    position = context.user_data['current_position']
    lat = context.user_data['current_coordinates']['lat']
    lon = context.user_data['current_coordinates']['lon']
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=WHERE_MSG+position)
    try:
        filename = 'position_' + update.effective_chat.username + '.png'
        map = igo.StaticMap(500, 500)
        map.add_marker(igo.CircleMarker((lon, lat), 'blue', 10))
        image = map.render()
        image.save(filename)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(filename, 'rb'))
        os.remove(filename)
    except Exception as e:
        # print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣: something went wrong while checking your current \
position')


def pos(update, context):
    place = str(context.arguments[0])
    context.user_data['current_position'] = place
    context.user_data['current_coordinates'] = {
        'lat': igo.ox.geocode(place)[0], 'lon': igo.ox.geocode(place)[1]}


# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('where', say_where))
dispatcher.add_handler(CommandHandler('pos', pos))
dispatcher.add_handler(MessageHandler(Filters.location, where))

# engega el bot
updater.start_polling()
