from utils import MessageSerialize
from bot.command import CommandPlugin

class Ping(CommandPlugin):
    pattern = r'ping'

    def run(self, msg: MessageSerialize, **kwargs):
        msg.reply(f'{msg.command.title()} Pong')
