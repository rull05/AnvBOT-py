import logging
import os
from neonize.client import NewClient
from neonize.utils import log

from .events import RunnerEvent
from utils import str_to_jid




class Runner(NewClient):
    def __init__(self, name: str, **kwargs):
        """
        Initializes a Runner object.

        :param name: The name of the bot.
        :type name: str
        :param kwargs: Additional keyword arguments.

        """
        # Create a sessions directory if it doesn't exist.
        if not os.path.exists('./sessions'):
            os.makedirs('./sessions')
        super().__init__(f'./sessions/{name}.sqlite3')
        self.bot_name = name
        self.event = RunnerEvent(self, dir_commands=kwargs.get('dir_commands'))
        log.setLevel(logging.INFO)
        self.owners = kwargs.get('owners', [])

    def run(self):
        self.connect()

    def group_metadata(self, chat: str):
        group_jid = str_to_jid(chat)
        return self.get_group_info(group_jid)

    
