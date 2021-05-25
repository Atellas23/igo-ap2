# importa l'API de Telegram
from telegram.ext import Updater, CommandHandler
import igo
import os
from datetime import date, datetime, timedelta
from urllib import request

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

def toca_descarregar(traffic_data: igo.Traffic_data):
    last_known_time = get_last_known_time(traffic_data)
    if last_known_time-datetime.now() >= timedelta(minutes=5):
        return True
    else:
        return False

def get_location_name(lat, lon):
    request_url = 'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}'.format(lat=lat, lon=lon)
    response = request.urlopen(request_url)
    lines = [l.decode('utf-8') for l in response.readlines()]
    for line in lines:
        print(line)
    # https://nominatim.openstreetmap.org/reverse?lat=<value>&lon=<value>&<params>

def start(update, context):
    GREETING = '''Welcome to IGO, the newest navigation tool to travel at light
    speed through Barcelona.'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=GREETING)
    lat, lon = update.message.location.latitude, update.message.location.longitude
    context.user_data['current_position'] = ????


def help(update, context):
    HELP_MSG = '''My commands are:
    - /author: Returns information from the project authors.
    - /go: Requires a location from the city of Barcelona and returns the shortest path from the users current location.
    - /where: Returns the users current location.
    - /pos: Requires a location from the city of Barcelona to make it become the new users current location.
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MSG)


def author(update, context):
    AUTHOR_MSG = '''This project's authors are:
    Àlex Batlle Casellas, Arenys de Munt, 2001.
    Pere Cornellà Franch, Fornells de la Selva, 2002.
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text=AUTHOR_MSG)

def go(update, context):
    destination = str(context.arguments[0])
    path = igo.build_ipath(graph, context.user_data['current_position'], destination)
    filename = 'path_'+update.effective_chat.username+'.png'
    igo.plot_path(graph, path, filename=filename)
    context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(filename, 'rb'))

def where(update, context):
    try:
        lat, lon = update.message.location.latitude, update.message.location.longitude
        # print(lat, lon)
        fitxer = 'position_' + update.effective_chat.username + '.png'
        mapa = igo.StaticMap(500, 500)
        mapa.add_marker(CircleMarker((lon, lat), 'blue', 10))
        imatge = mapa.render()
        imatge.save(fitxer)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(fitxer, 'rb'))
        os.remove(fitxer)
    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣')

def say_where():
    WHERE_MSG = '''You are currently at'''
    pass


def pos(update, context):
    context.user_data['current_position'] = str(context.arguments[0])



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
