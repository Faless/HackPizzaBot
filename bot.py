# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

from telegram import ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater
from includes import User, Event, Order
from handlers import start_handler, event_handler, add_event_handler, order_handler, add_order_handler, help_handler
from database import init_db, add_user, add_event, add_order, list_events, list_users, list_orders, get_event, get_user, get_order, archive_event, del_order

import logging


def main(debug=False):
  level = logging.DEBUG if debug else logging.INFO
  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)
  init_db()
  token=""
  try:
    with open(".token", 'r') as f:
      token=f.readline().replace("\n", "")
  except:
    print("Token not found...")
    sys.exit(1)
  
  print("Connecting...")
  updater = Updater(token=token)
  print("Connected")
  dispatcher = updater.dispatcher
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(event_handler)
  dispatcher.add_handler(order_handler)
  dispatcher.add_handler(help_handler)
  dispatcher.add_handler(add_event_handler)
  dispatcher.add_handler(add_order_handler)

  print("Start polling...")
  updater.start_polling()

  print("Idle...")
  updater.idle()



if __name__=='__main__':
  # Argument parsing
  import argparse
  parser = argparse.ArgumentParser(description='HackPizzaBot.\nPizza scheduling powered by the power of robots!')
  parser.add_argument('-d', '--debug', action='store_true', help="Enable debug information")
  args = parser.parse_args()

  # Run bot
  main(debug=args.debug)

#"""
#Use a custom keyboard
#"""
#keyboard = [
#    ['Add Event'],
#    ['Add Pizza'],
#    ['Add Drinks'],
#    ['List Events']
#]
#reply_markup = ReplyKeyboardMarkup(keyboard)

#bot.send_message(user_id, 'please enter a number', reply_markup=reply_markup).wait()
