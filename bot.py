# importa l'API de Telegram
from telegram.ext import Updater, CommandHandler
import igo

# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start

GREETING = 'hola!'
HELP_MSG = '''
Les meves comandes són:
- /start:
- /help:
- /
'''


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=GREETING)


def bot_help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MSG)


def author(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=GREETING)


def go(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=GREETING)


def where(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=GREETING)


def pos(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=GREETING)


# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', bot_help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(CommandHandler('pos', pos))

# engega el bot
updater.start_polling()
