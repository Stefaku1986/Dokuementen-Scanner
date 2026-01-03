import logging
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .stable_write import wait_for_stable_file

logger = logging.getLogger(__name__)


class HotfolderHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[Path], None]):
        self.callback = callback

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        logger.info("Neue Datei erkannt: %s", path)
        if wait_for_stable_file(path):
            self.callback(path)
        else:
            logger.warning("Datei wurde nicht stabil: %s", path)


def watch_directory(path: Path, callback: Callable[[Path], None]):
    observer = Observer()
    handler = HotfolderHandler(callback)
    observer.schedule(handler, str(path), recursive=False)
    observer.start()
    logger.info("Watcher gestartet auf %s", path)
    return observer
