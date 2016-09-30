from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, Filters, RegexHandler
from telegram import ReplyKeyboardMarkup
from database import list_events, add_event, get_event
from includes import Event, User, Order

ConvStore = {}

NEW_NAME, NEW_CONFIRM = range(2)

def cancel(bot, update):
  bot.sendMessage(chat_id=update.message.chat_id, text="Mission aborted!")
  return ConversationHandler.END

def start(bot, update):
  bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def events(bot, update):
  events = list_events()
  bot.sendMessage(chat_id=update.message.chat_id, text="Event List:\n%s" % ("\n".join([str(e) for e in events]) if len(events) > 0 else "No events"))


def new_event(bot, update):
  update.message.reply_text("Please select the name for the new event or type /cancel to abort")
  return NEW_NAME

def new_event_name(bot, update):
  name = update.message.text
  if len(name) < 3:
    update.message.reply_text(text="Invalid name, must be at least 3 chars")
    return NEW_NAME
  ConvStore[update.message.from_user.id] = name
  reply_keyboard = [['YES', 'NO']]
  update.message.reply_text("The event name will be: %s" % name, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
  return NEW_CONFIRM

def new_event_confirm(bot, update):
  if update.message.text != "YES":
    return NEW_NAME
  name = ConvStore.pop(update.message.from_user.id, None)
  if name is None:
    return NEW_NAME

  add_event(Event(eid=None, name=name, archive=0))
  update.message.reply_text("Event with name: \"%s\" has been created" % name)
  return ConversationHandler.END

start_handler = CommandHandler('start', start)
event_handler = CommandHandler('events', events)

#add_event_handler = CommandHandler('new', add_event, pass_args=True)
add_event_handler = ConversationHandler(
        entry_points=[CommandHandler('new', new_event)],

        states={
            NEW_NAME: [MessageHandler([Filters.text], new_event_name)],

            NEW_CONFIRM: [RegexHandler('^(YES|NO)$', new_event_confirm)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
);


