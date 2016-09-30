from telegram.ext import CommandHandler, ConversationHandler
from database import list_events

def start(bot, update):
  bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def events(bot, update):
  events = list_events()
  bot.sendMessage(chat_id=update.message.chat_id, text="Event List:\n%s" % "\n".join(get_events()) if len(events) > 0 else "No events")

start_handler = CommandHandler('start', start)
event_handler = CommandHandler('events', events)


