import importlib.util
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ModuleReloader(FileSystemEventHandler):
    def __init__(self, directory):
        super().__init__()
        self.modules = {}
        self.directory = directory

    def load_module(self, file_path):
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.modules[module_name] = module
        print(f"Module {module_name} loaded.")

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}")
            module_name = os.path.splitext(os.path.basename(event.src_path))[0]
            if module_name in self.modules:
                del self.modules[module_name]  # Remove existing module from cache
            self.load_module(event.src_path)

    def watch(self):
        observer = Observer()
        observer.schedule(self, self.directory, recursive=True)
        observer.start()
        print(f"Watching directory {directory} for Python file changes...")
