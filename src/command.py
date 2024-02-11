import os
import re
import importlib
import inspect
from typing import List, TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from utils import MessageSerialize


if TYPE_CHECKING:
    from src.core import Runner
    from neonize.events import MessageEv
    from utils.wa_classes import Message


def check_method(cls, method_name):
    method = getattr(cls, method_name)
    if not inspect.isfunction(method):
        raise AttributeError(f"'{method_name}' must be a method. not a {type(method)}.")


def check_attribute(cls, attr_name):
    if not hasattr(cls, attr_name):
        raise AttributeError(f"Subclass {cls.__name__} must have a '{attr_name}' attribute.")


def check_type(cls, attr_name, expected_type):
    attr = getattr(cls, attr_name)
    if not isinstance(attr, expected_type):
        raise TypeError(f"Subclass {cls.__name__} '{attr_name}' attribute must be a {expected_type}. not a {type(attr)}.")


def is_method_overridden(_cls, instance, method_name):
    """Check if a method is overridden in a subclass."""
    if not hasattr(instance, method_name):
        return False
    func_method = getattr(instance, method_name)
    cls_method = getattr(_cls, method_name)
    if func_method.__code__ is cls_method.__code__:
        return False
    return True


class CommandBase(ABC):
    """
    Base class for command plugins.
    """
    desc: str = ''
    owner_only: bool = False
    group_only: bool = False
    private_only: bool = False
    group_admin: bool = False
    group_owner: bool = False

    def before(self, msg: MessageSerialize) -> bool:
        pass

    @abstractmethod
    def execute(self, msg: MessageSerialize) -> any:
        pass

    def after(self, msg: MessageSerialize, **kwargs) -> None:
        pass

    @classmethod
    def set_attr(cls, name: str, value: any) -> None:
        setattr(cls, name, value)

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, 'name'):
            cls.name = cls.__name__

        if hasattr(cls, 'on_message'):
            check_method(cls, 'on_message')
        elif hasattr(cls, 'before'):
            check_method(cls, 'before')
        elif hasattr(cls, 'execute'):
            check_method(cls, 'execute')
            check_attribute(cls, 'pattern')
            check_type(cls, 'pattern', (str, re.Pattern))
            if hasattr(cls, 'prefix'):
                check_type(cls, 'prefix', (str, re.Pattern))
        else:
            raise AttributeError(f"Subclass {cls.__name__} must have a 'on_message', 'before' or 'execute' method.")

        if hasattr(cls, 'after'):
            if not hasattr(cls, 'execute'):
                raise AttributeError(f"Subclass {cls.__name} must have a 'execute' method. if it has 'after' method.")
            check_method(cls, 'after')


class CommandHandler:
    """
    A class that handles commands and executes corresponding plugins.
    """

    def __init__(self, directory: str) -> None:
        """
        Initialize the CommandHandler.

        :param directory: The directory of the command plugins.
        """
        print('Initializing CommandHandler...')
        self._plugins: List[CommandBase] = []
        self._dir: str = directory
        self._prefix_pattern: re.Pattern = re.compile(r'^!', re.IGNORECASE)
        self._load_all_plugin()
        self._observer = Observer()
        self._observer.schedule(ReloadHandler(self._plugin_observer), self._dir, recursive=False)
        self._observer.start()

    def handle(self, runner: 'Runner', message: 'MessageEv') -> None:
        """
        Handles the incoming command message.

        :param runner: The instance of the Runner.
        :param message: The incoming message.
        """
        msg: Message = MessageSerialize(runner, message).serialize()
        if msg.is_bot:
            return

        for _, plugin in self._plugins:
            # check if plugin has implemented on_message method and not base class
            if is_method_overridden(CommandBase, plugin, 'on_message'):
                plugin.on_message(msg)
                break

            _prefix_pattern = self._prefix_pattern

            if hasattr(plugin, 'prefix') and plugin.prefix:
                _prefix_pattern = plugin.prefix

            if isinstance(_prefix_pattern, str):
                _prefix_pattern = re.compile(_prefix_pattern, re.IGNORECASE)

            if match_prefix := _prefix_pattern.search(msg.text):
                no_prefix: str = msg.text.replace(match_prefix[0], '').strip()
                command, *args = no_prefix.split(' ')
                command_text: str = ' '.join(args)
                command_pattern: re.Pattern = re.compile(plugin.pattern, re.IGNORECASE)

                if match_command := command_pattern.search(command):
                    if mid_text := self._validate(plugin, msg):
                        if isinstance(mid_text, str):
                            msg.reply(mid_text)
                            break
                    msg.command = match_command[0]
                    msg.args = args
                    msg.body = command_text
                    msg.used_prefix = match_prefix[0]

                    if is_method_overridden(CommandBase, plugin, 'before'):
                        if not plugin.before(msg):
                            break
                    plugin_resp = plugin.execute(msg)
                    if plugin_resp:
                        if is_method_overridden(CommandBase, plugin, 'after'):
                            plugin.after(msg, plugin_resp)
                        else:
                            print('WARNING: Plugin response not handled.')

                    return

    def _validate(self, plugin: CommandBase, msg: MessageSerialize) -> None:
        if plugin.owner_only and not msg.is_owner:
            return 'Hanya owner yang bisa menggunakan perintah ini.'
        if plugin.group_only and not msg.is_group:
            return 'Perintah ini hanya bisa digunakan di grup.'
        if plugin.private_only and msg.is_group:
            return 'Perintah ini hanya bisa digunakan di chat pribadi.'
        if plugin.group_admin and not msg.is_admin:
            return 'Hanya admin grup yang bisa menggunakan perintah ini.'
        if plugin.group_owner and not msg.is_owner:
            return 'Hanya owner grup yang bisa menggunakan perintah ini.'
        return None

    def _load_all_plugin(self) -> None:
        for file_name in os.listdir(self._dir):
            if file_name.endswith('.py'):
                plugin_name: str = os.path.splitext(file_name)[0]
                module_path: str = f"{self._dir}.{plugin_name}"
                self._add_plugin(module_path, plugin_name)
                print('Loaded plugin', plugin_name)

    def _get_plugin(self, module) -> Optional[CommandBase]:
        try:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if inspect.isclass(attr) and issubclass(attr, CommandBase) and attr != CommandBase:   
                    return attr
                    break
        except Exception as e:
            raise e

    def _append_plugin(self, module, command_cls: CommandBase) -> None:
        _,plugin_name = module.__name__.split('.')
        command_cls.set_attr('name', plugin_name)
        self._plugins.append([module, command_cls()])


    def _add_plugin(self, module_path: str, plugin_name: str) -> None:
        try:
            module = importlib.import_module(module_path)
            command_cls: CommandBase = self._get_plugin(module)
            self._append_plugin(module, command_cls)
        except Exception as e:
            print('Failed to load plugin:', e)

    def _plugin_observer(self, event: FileSystemEventHandler) -> None:
        """
        Observe plugin directory for changes.

        :param event: The event triggered by the file system change.
        """
        file_name: str = os.path.basename(event.src_path)
        plugin_name: str = os.path.splitext(file_name)[0]
        module_path: str = f"{self._dir}.{plugin_name}"
        if event.event_type == 'deleted':
            for plugin in self._plugins:
                module, cmd_cls = plugin
                if cmd.name == plugin_name:
                    self._plugins.remove(plugin)
                    break
        if event.event_type == 'created':
            self._add_plugin(module_path, plugin_name)
        if event.event_type == 'modified':
            for plugin in self._plugins:
                module, command_cls = plugin
                if command_cls.name == plugin_name:
                    self._plugins.remove(plugin)
                    reload_mod = importlib.reload(module)
                    command_cls = self._get_plugin(reload_mod)
                    self._append_plugin(reload_mod, command_cls)
                    print('Reloaded plugin', command_cls.name)
                    break


class ReloadHandler(FileSystemEventHandler):
    """
    Watchdog event handler for reloading plugins.
    """
    def __init__(self, reload_callback: callable) -> None:
        self._reload_callback: callable = reload_callback

    def on_any_event(self, event: FileSystemEventHandler) -> None:
        self._reload_callback(event)
