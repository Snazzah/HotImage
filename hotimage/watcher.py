import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
log = logging.getLogger(__name__)

class ImageObserveEventHandler(FileSystemEventHandler):
    def __init__(self, instance, path):
        super(ImageObserveEventHandler, self).__init__()
        self._instance = instance
        self._path = path

    def on_moved(self, event):
        if event.is_directory:
            log.debug('%s was moved. Refreshing cache...', event.src_path)
            self._instance._load_images()

    def on_created(self, event):
        category = os.path.relpath(event.src_path, self._path)
        filename = None
        if not event.is_directory:
            category, filename = os.path.split(category)

        log.debug('The folder (or a file in the folder) for the category %s was created. Refreshing cache...', category)
        self._instance._load_images()

    def on_deleted(self, event):
        category = os.path.relpath(event.src_path, self._path)
        filename = None
        if not event.is_directory:
            category, filename = os.path.split(category)

        log.debug('The folder (or a file in the folder) for the category %s was deleted. Refreshing cache...', category)
        self._instance._load_images()

    def on_modified(self, event):
        category = os.path.relpath(event.src_path, self._path)
        filename = None
        if not event.is_directory:
            category, filename = os.path.split(category)

        log.debug('The folder (or a file in the folder) for the category %s was modified. Refreshing cache...', category)
        self._instance._load_images()

def observe_images(path, instance):
    observer = Observer()
    observer.schedule(ImageObserveEventHandler(instance, path), path, recursive=True)
    observer.start()
    return observer

class ConfigObserveEventHandler(FileSystemEventHandler):
    def __init__(self, instance):
        super(ConfigObserveEventHandler, self).__init__()
        self._instance = instance

    def on_moved(self, event):
        if event.src_path == './config.json':
            log.warn(f'config.json was moved to "{event.dest_path}"! Make sure this is solved before you restart the instance!')
        elif event.dest_path == './config.json':
            log.debug(f'"{event.dest_path}" moved to config.json. Reloading config...')
            self._instance.config = self._instance._load_config()

    def on_created(self, event):
        if event.src_path == './config.json':
            log.debug('config.json was created. Reloading config...')
            self._instance.config = self._instance._load_config()

    def on_deleted(self, event):
        if event.src_path == './config.json':
            log.warn('config.json was deleted! Make sure this is solved before you restart the instance!')

    def on_modified(self, event):
        if event.src_path == './config.json':
            log.debug('config.json was modified. Reloading config...')
            self._instance.config = self._instance._load_config()

def observe_config(instance):
    observer = Observer()
    observer.schedule(ConfigObserveEventHandler(instance), '.')
    observer.start()
    return observer