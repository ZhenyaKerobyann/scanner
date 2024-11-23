# logviewer/file_monitor.py
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from config.settings import LOGGING


class LogFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.file = open(LOGGING['handlers']['file_thread']['filename'], 'r')
        self.file.seek(0, os.SEEK_END)

    def on_modified(self, event):
        if event.src_path == LOGGING['handlers']['file_thread']['filename']:
            for line in self.file:
                async_to_sync(self.channel_layer.group_send)(
                    "logs",
                    {
                        "type": "log_message",
                        "message": line.strip(),
                    }
                )


def start_log_monitor():
    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(LOGGING['handlers']['file_thread']['filename']),
                      recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
