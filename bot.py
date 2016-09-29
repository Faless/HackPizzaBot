# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import Updater

import logging


def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)

def main(debug=False):
  level = logging.DEBUG if debug else logging.INFO
  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)
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
