from dotenv import load_dotenv
from bot import Runner
import os

load_dotenv()


BOT_NAME = os.environ.get('BOT_NAME') or 'Anv'
DIR_COMMANDS = os.environ.get('DIR_COMMANDS') or 'commands/'

def main():
    bot = Runner(os.environ.get('BOT_NAME'), dir_commands=DIR_COMMANDS)
    bot.run()



if __name__ == '__main__':
    main()