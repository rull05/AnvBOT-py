# This file contains the configuration for the bot

import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME: str = os.environ.get('BOT_NAME', 'anv')
DIR_COMMANDS: str = os.environ.get('DIR_COMMANDS', 'commands')
BOT_PREFIX: str = os.environ.get('PREFIX', '!')

__all__ = ['BOT_NAME', 'DIR_COMMANDS', 'BOT_PREFIX']