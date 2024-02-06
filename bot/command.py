import os
import re
import importlib
import inspect
from abc import ABC, abstractmethod
from neonize.events import MessageEv
from neonize.client import NewClient

from utils import MessageSerialize


class CommandPlugin(ABC):
    description = ''

    @abstractmethod
    def run(self):
        raise NotImplementedError('This method must be implemented by subclasses')

    @classmethod
    def set_attr(cls, name, value):
        setattr(cls, name, value)


class CommandHandler:
    def __init__(self, directory: str):
        self.plugins = []
        self.dir = directory
        self.prefix_pattern = re.compile(r'^!', re.IGNORECASE)
        self._load_plugins()

    def _load_plugins(self):
        for file_name in os.listdir(self.dir):
            if file_name.endswith('.py'):
                plugin_name = os.path.splitext(file_name)[0]
                module_path = f"{self.dir}.{plugin_name}"
                try:
                    module = importlib.import_module(module_path)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if inspect.isclass(attr) and issubclass(attr, CommandPlugin) and attr != CommandPlugin:
                            plugin_name = getattr(attr, 'name', attr.__name__)
                            attr.set_attr('name', plugin_name)
                            self.plugins.append(attr())
                            print('Loaded plugin', attr.name)
                            break
                except Exception as e:
                    print(f"Failed to load plugin {plugin_name}: {e}")

    def handle(self, runner: NewClient, message: MessageEv):
        msg = MessageSerialize(runner, message)
        if msg.is_from_me: return
        match_str = self.prefix_pattern.search(msg.text)
        if match_str:
            no_prefix = msg.text.replace(match_str[0], '').strip()
            command, *args = no_prefix.split(' ')
            text = ' '.join(args)
            for plugin in self.plugins:
                if plugin.run:
                    command_pattern = re.compile(plugin.pattern, re.IGNORECASE)
                    match_command = command_pattern.search(command)
                    if match_command:
                        msg.set_attr(command=match_command[0], args=args, body=text)
                        plugin.run(msg)
