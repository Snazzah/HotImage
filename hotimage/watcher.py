import os
import time
import logging
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
log = logging.getLogger(__name__)


def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator


class ImageObserveEventHandler(FileSystemEventHandler):
    def __init__(self, instance, path):
        super(ImageObserveEventHandler, self).__init__()
        self._instance = instance
        self._path = path
        self._actions_count = 0
        self._waiting_to_reload = False

    def on_moved(self, event):
        if event.is_directory:
            log.debug('%s was moved.', event.src_path)
            self._load_images()

    def on_created(self, event):
        category = os.path.relpath(event.src_path, self._path)
        filename = None
        if not event.is_directory:
            category, filename = os.path.split(category)

        log.debug('The folder (or a file in the folder) for the category %s was created.', category)
        self._load_images()

    def on_deleted(self, event):
        category = os.path.relpath(event.src_path, self._path)
        filename = None
        if not event.is_directory:
            category, filename = os.path.split(category)

        log.debug('The folder (or a file in the folder) for the category %s was deleted.', category)
        self._load_images()

    def on_modified(self, event):
        category = os.path.relpath(event.src_path, self._path)
        filename = None
        if not event.is_directory:
            category, filename = os.path.split(category)

        log.debug('The folder (or a file in the folder) for the category %s was modified.', category)
        self._load_images()
    
    # A way of debouncing image changes
    @debounce(5)
    def _load_images(self):
        log.info('Images changes finished. Refreshing cache...')
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
        self._checking_filesize = False

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
            log.debug('config.json was modified.')
            self._instance.config = self._instance._load_config()
            
            if not self._checking_filesize:
                log.info('Detected change in config.json, Waiting for configuration to finish loading...')
                self._checking_filesize = True
                file_size = -1
                while file_size != os.path.getsize('./config.json'):
                    file_size = os.path.getsize('./config.json')
                    time.sleep(1)
                self._checking_filesize = False
                log.info('config.json finished loading. Reloading config...')
                self._instance.config = self._instance._load_config()

def observe_config(instance):
    observer = Observer()
    observer.schedule(ConfigObserveEventHandler(instance), '.')
    observer.start()
    return observer