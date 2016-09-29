# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import Updater

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)

def main():
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
  main()

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
