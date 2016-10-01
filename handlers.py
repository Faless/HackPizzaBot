from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, Filters, RegexHandler
from telegram import ReplyKeyboardMarkup
from database import list_events, add_event, get_event, add_order, list_orders, get_order, add_user, get_user
from includes import Event, User, Order

YesNoKbd = ReplyKeyboardMarkup([['YES', 'NO']], one_time_keyboard=True)

class Storage:

  def __init__(self):
    self.storage = {}

  def set(self, chat_id, user_id, data):
    if not chat_id in self.storage:
      self.storage[chat_id] = {}
    if not user_id in self.storage[chat_id]:
      self.storage[chat_id][user_id] = {}

    self.storage[chat_id][user_id] = data

  def get(self, chat_id, user_id, default=None):
    if not chat_id in self.storage:
      return default
    if not user_id in self.storage[chat_id]:
      return default

    return self.storage[chat_id][user_id]

  def remove(self, chat_id, user_id):
    if not chat_id in self.storage:
      return
    if not user_id in self.storage[chat_id]:
      return
    del self.storage[chat_id][user_id]
    if len(self.storage[chat_id]) == 0:
      del self.storage[chat_id]


class BaseHandler(object):

  def __init__(self):
    self.storage = Storage()
    self.handlers = []

  def cancel(self, bot, update, msg="Mission aborted!"):
    bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    self.storage.remove(update.message.chat_id, update.message.from_user.id)
    return ConversationHandler.END

  def register(self, dispatcher):
    for h in self.handlers:
      dispatcher.add_handler(h)


class MiscHandler(BaseHandler):
  def __init__(self):
    super(MiscHandler, self).__init__()

    self.handlers.append(CommandHandler('help', self.show_help))
    self.handlers.append(CommandHandler('start', self.start_bot))

  def show_help(self, bot, update):
    msg = "The HackPizzaBot is proud to present... the pizza manager!\n\n"
    msg+= "/help\t- Show this help\n"
    msg+= "/new\t- Create a new event\n"
    msg+= "/events\t- Lists currently scheduled events\n"
    msg+= "/order\t- Create a new order for an event\n"
    msg+= "/orders\t- Lists currently scheduled events followed by relative orders\n"
    msg+= "/cancel\t- Will cancel any active conversion with the HackPizzaBot\n"
    bot.sendMessage(chat_id=update.message.chat_id, text=msg)

  def start_bot(self, bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="The HackPizzaBot is proud to present... the pizza manager!\n\nType /help for available commands")


class EventHandler(BaseHandler):
  NEW_NAME, NEW_CONFIRM = range(2)

  def __init__(self):
    super(EventHandler, self).__init__()

    self.handlers.append(CommandHandler('events', self.get_all))

    self.handlers.append(ConversationHandler(
        entry_points=[CommandHandler('new', self.create_start)],

        states={
            EventHandler.NEW_NAME: [MessageHandler([Filters.text], self.select_name)],

            EventHandler.NEW_CONFIRM: [RegexHandler('^(YES|NO)$', self.create_end)],
        },

        fallbacks=[CommandHandler('cancel', self.cancel)])
    )


  def get_all(self, bot, update):
    events = list_events()
    bot.sendMessage(chat_id=update.message.chat_id, text="Event List:\n%s" % ("\n".join([str(e) for e in events]) if len(events) > 0 else "No events"))

  def create_start(self, bot, update):
    update.message.reply_text("Please select the name for the new event or type /cancel to abort")
    return EventHandler.NEW_NAME

  def select_name(self, bot, update):
    name = update.message.text
    if len(name) < 3:
      update.message.reply_text(text="Invalid name, must be at least 3 chars")
      return self.create_start(bot, update)
    self.storage.set(update.message.chat_id, update.message.from_user.id, name)
    update.message.reply_text("The event name will be: %s" % name, reply_markup=YesNoKbd)
    return EventHandler.NEW_CONFIRM

  def create_end(self, bot, update):
    if update.message.text != "YES":
      return self.create_start(bot,update)
    name = self.storage.get(update.message.chat_id, update.message.from_user.id, None)
    if name is None:
      return self.create_start(bot,update)

    self.storage.remove(update.message.chat_id, update.message.from_user.id)
  
    add_event(Event(eid=None, name=name, archive=0))
    update.message.reply_text("Event with name: \"%s\" has been created" % name)
    return ConversationHandler.END


class OrderHandler(BaseHandler):

  NEW_EVENT_SELECT, NEW_NAME, NEW_CONFIRM = range(3)

  def __init__(self):
    super(OrderHandler, self).__init__()
    self.handlers.append(CommandHandler("orders", self.get_all))
    self.handlers.append(ConversationHandler(
        entry_points=[CommandHandler('order', self.create_start)],

        states={
            OrderHandler.NEW_EVENT_SELECT: [RegexHandler('^[0-9]+$', self.select_event)],

            OrderHandler.NEW_NAME: [MessageHandler([Filters.text], self.select_name)],

            OrderHandler.NEW_CONFIRM: [RegexHandler('^(YES|NO)$', self.create_end)],
        },

        fallbacks=[CommandHandler('cancel', self.cancel)])
    )

  def get_all(self, bot, update):
    events = list_events()
    msg = "Orders list:"
    for evt in events:
      ords = list_orders(evt.eid)
      msg+="\n\n%s:" % evt
      for o in ords:
        msg+="\n   @%s - %s" % (ords[o]["user"].nick, ords[o]["order"].data)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg)

  def create_start(self, bot, update):
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
    return OrderHandler.NEW_EVENT_SELECT

  def select_event(self, bot, update):
    name = update.message.text
    eid = 0
    try:
      eid = int(name)
      if get_event(eid) == None:
         update.message.reply_text("Invalid event id")
         return self.cancel(bot,update)
    except:
         return self.cancel(bot,update)
    if get_order(eid, update.message.from_user.id) is not None:
      update.message.reply_text("You already placed an order for this event")
      return self.cancel(bot,update)
    self.storage.set(update.message.chat_id, update.message.from_user.id, {"eid": eid})
    update.message.reply_text("Please specify the order for event %s or type /cancel to abort" % eid)
    return OrderHandler.NEW_NAME

  def select_name(self, bot, update):
    name = update.message.text
    if len(name) < 3:
      update.message.reply_text(text="Invalid order, must be at least 3 chars")
      return OrderHandler.NEW_NAME
    data = self.storage.get(update.message.chat_id, update.message.from_user.id)
    if data is None:
      return self.cancel(bot,update)
    data["order"] = name
    self.storage.set(update.message.chat_id, update.message.from_user.id, data)
    reply_keyboard = [['YES', 'NO']]
    update.message.reply_text("Your order will be: %s" % name, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return OrderHandler.NEW_CONFIRM
  
  def create_end(self, bot, update):
    if update.message.text != "YES":
      return OrderHandler.NEW_NAME
    data = self.storage.get(update.message.chat_id, update.message.from_user.id)
    if data is None:
      return OrderHandler.NEW_NAME
  
    user = update.message.from_user
    if get_user(user.id) is None:
      add_user(User(uid=user.id, name=user.first_name, nick=user.username))
  
    add_order(Order(eid=data["eid"], uid=update.message.from_user.id, data=data["order"]))
    update.message.reply_text("Order added to event %s: \"%s\"" % (data["eid"], data["order"]))
    self.storage.remove(update.message.chat_id, update.message.from_user.id)
    return ConversationHandler.END
  
