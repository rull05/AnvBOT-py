
import re
from dataclasses import dataclass

from src.command import CommandBase
from utils import MessageSerialize

class Debug(CommandBase):
    prefix: str = r'^=?>'
    pattern: str = r'(.*)'
    desc: str = 'Debug the bot'
    owner_only: bool = True

    def execute(self, msg: MessageSerialize):
        code = re.sub(r'^=?>', '', msg.text).strip()
        if not code:
            return msg.reply('No code provided')
        try:
            result = eval(code)
            msg.reply(str(result))
        except Exception as e:
            msg.reply(str(e))
            
