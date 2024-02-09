from src import Runner
from src.config import BOT_NAME, DIR_COMMANDS


def main():
    
    bot = Runner(BOT_NAME, dir_commands=DIR_COMMANDS)
    bot.run()


if __name__ == '__main__':
    main()