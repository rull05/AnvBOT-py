from typing import Type, Callable
from neonize.events import Event, EventType, MessageEv, CallOfferEv, EVENT_TO_INT, ConnectedEv
from neonize import proto
from neonize.utils import log
from neonize.client import NewClient

from .command import CommandHandler

class RunnerEvent(Event):
    def __init__(self, runner, **kwargs):
        super().__init__(runner)
        self.dir_commands = kwargs.get('dir_commands')
        self.command_handler = CommandHandler(self.dir_commands)
        self.register()

    def on_message(self, runner: NewClient, message: MessageEv):
        self.command_handler.handle(runner, message)


    def on_call(self, runner: NewClient, call: CallOfferEv):
        log.debug(call)

    def on_connected(self, runner: NewClient, __: ConnectedEv):
        log.info('Bot Connected!')

    def register(self):
        self._register_event(MessageEv, self.on_message)
        self._register_event(CallOfferEv, self.on_call)
        self._register_event(ConnectedEv, self.on_connected)

    def _register_event(self, event: Type[EventType], func: Callable):
        wrapped_func = super().wrap(func, event)
        self.list_func.update({EVENT_TO_INT[event]: wrapped_func})
    