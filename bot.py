from telegram.ext import Updater
from database import init_db
from handlers import EventHandler, OrderHandler, MiscHandler

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

  eventhandler = EventHandler()
  eventhandler.register(dispatcher)
  orderhandler = OrderHandler()
  orderhandler.register(dispatcher)
  mischandler = MiscHandler()
  mischandler.register(dispatcher)
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

