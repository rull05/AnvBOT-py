
import logging
from neonize.client import NewClient
from neonize.events import MessageEv
from neonize.utils import log

from .events import RunnerEvent


class Runner(NewClient):

    def __init__(self, name, **kwargs):
        super().__init__(name + '.sqlite3')
        self.bot_name = name
        self.event = RunnerEvent(self, dir_commands=kwargs.get('dir_commands'))
        log.setLevel(logging.INFO)
    def run(self):
        
        self.connect()


    