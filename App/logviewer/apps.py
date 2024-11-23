# logviewer/apps.py
from django.apps import AppConfig
import threading
from .file_monitor import start_log_monitor


class LogviewerConfig(AppConfig):
    name = 'logviewer'

    def ready(self):
        thread = threading.Thread(target=start_log_monitor)
        thread.daemon = True
        thread.start()
