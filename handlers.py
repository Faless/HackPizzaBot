from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, Filters, RegexHandler
from telegram import ReplyKeyboardMarkup
from database import list_events, add_event, get_event, add_order, list_orders, get_order, add_user, get_user
from includes import Event, User, Order

ConvStore = {}

EVENT_NAME, EVENT_CONFIRM = range(2)
ORDER_EVENT, ORDER_NAME, ORDER_CONFIRM = range(3) 

def show_help(bot, update):
  msg = "The HackPizzaBot is proud to present... the pizza manager!\n\n"
  msg+= "/help\t- Show this help\n"
  msg+= "/new\t- Create a new event\n"
  msg+= "/events\t- Lists currently scheduled events\n"
  msg+= "/order\t- Create a new order for an event\n"
  msg+= "/orders\t- Lists currently scheduled events followed by relative orders\n"
  msg+= "/cancel\t- Will cancel any active conversion with the HackPizzaBot\n"
  bot.sendMessage(chat_id=update.message.chat_id, text=msg)

def cancel(bot, update):
  bot.sendMessage(chat_id=update.message.chat_id, text="Mission aborted!")
  return ConversationHandler.END

def start(bot, update):
  bot.sendMessage(chat_id=update.message.chat_id, text="The HackPizzaBot is proud to present... the pizza manager!\n\nType /help for available commands")


def events(bot, update):
  events = list_events()
  bot.sendMessage(chat_id=update.message.chat_id, text="Event List:\n%s" % ("\n".join([str(e) for e in events]) if len(events) > 0 else "No events"))


def orders(bot, update):
  events = list_events()
  msg = "Orders list:"
  for evt in events:
    ords = list_orders(evt.eid)
    msg+="\n\n%s:" % evt
    for o in ords:
      msg+="\n   @%s - %s" % (ords[o]["user"].nick, ords[o]["order"].data)
  bot.sendMessage(chat_id=update.message.chat_id, text=msg)

def new_event(bot, update):
  update.message.reply_text("Please select the name for the new event or type /cancel to abort")
  return EVENT_NAME

def new_event_name(bot, update):
  name = update.message.text
  if len(name) < 3:
    update.message.reply_text(text="Invalid name, must be at least 3 chars")
    return EVENT_NAME
  ConvStore[update.message.from_user.id] = name
  reply_keyboard = [['YES', 'NO']]
  update.message.reply_text("The event name will be: %s" % name, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
  return EVENT_CONFIRM

def new_event_confirm(bot, update):
  if update.message.text != "YES":
    return EVENT_NAME
  name = ConvStore.pop(update.message.from_user.id, None)
  if name is None:
    return EVENT_NAME

  add_event(Event(eid=None, name=name, archive=0))
  update.message.reply_text("Event with name: \"%s\" has been created" % name)
  return ConversationHandler.END

def new_order(bot, update):
  msg = "Event List:"
  evts = list_events()
  i = 0
  j = 0
  reply_keyboard = [[]]
  for evt in evts:
    if i == 2:
      i=0
      j+=1
      reply_keyboard.append([])
    reply_keyboard[j].append(str(evt.eid))
    msg += "\n%s" % evt
    i+=1
  update.message.reply_text("%s\nPlease select the event you want to place an order for or /cancel to abort" % msg, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
  return ORDER_EVENT

def new_order_event(bot, update):
  name = update.message.text
  eid = 0
  try:
    eid = int(name)
    if get_event(eid) == None:
       update.message.reply_text("Invalid event id")
       return cancel(bot,update)
  except:
       return cancel(bot,update)
  if get_order(eid, update.message.from_user.id) is not None:
    update.message.reply_text("You already placed an order for this event")
    return cancel(bot,update)
  ConvStore[update.message.from_user.id] = {"eid": eid}
  update.message.reply_text("Please specify the order for event %s or type /cancel to abort" % eid)
  return ORDER_NAME

def new_order_name(bot, update):
  name = update.message.text
  if len(name) < 3:
    update.message.reply_text(text="Invalid order, must be at least 3 chars")
    return ORDER_NAME
  ConvStore[update.message.from_user.id]["order"] = name
  reply_keyboard = [['YES', 'NO']]
  update.message.reply_text("Your order will be: %s" % name, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
  return ORDER_CONFIRM

def new_order_confirm(bot, update):
  if update.message.text != "YES":
    return ORDER_NAME
  data = ConvStore.pop(update.message.from_user.id, None)
  if data is None:
    return ORDER_NAME

  user = update.message.from_user
  if get_user(user.id) is None:
    add_user(User(uid=user.id, name=user.first_name, nick=user.username))

  add_order(Order(eid=data["eid"], uid=update.message.from_user.id, data=data["order"]))
  update.message.reply_text("Order added to event %s: \"%s\"" % (data["eid"], data["order"]))
  return ConversationHandler.END



start_handler = CommandHandler('start', start)
event_handler = CommandHandler('events', events)
order_handler = CommandHandler('orders', orders)
help_handler = CommandHandler('help', show_help)

add_event_handler = ConversationHandler(
        entry_points=[CommandHandler('new', new_event)],

        states={
            EVENT_NAME: [MessageHandler([Filters.text], new_event_name)],

            EVENT_CONFIRM: [RegexHandler('^(YES|NO)$', new_event_confirm)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
);

add_order_handler = ConversationHandler(
        entry_points=[CommandHandler('order', new_order)],

        states={
            ORDER_EVENT: [RegexHandler('^[0-9]+$', new_order_event)],

            ORDER_NAME: [MessageHandler([Filters.text], new_order_name)],

            ORDER_CONFIRM: [RegexHandler('^(YES|NO)$', new_order_confirm)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
);

