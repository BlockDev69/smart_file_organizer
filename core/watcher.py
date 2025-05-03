import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileWatcher(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback  # Fonction à appeler lors d'un changement
        
    def on_created(self, event):
        """Détecte les nouveaux fichiers ajoutés"""
        if not event.is_directory:
            self.callback(event.src_path)
            
    def on_modified(self, event):
        """Détecte les fichiers modifiés"""
        if not event.is_directory:
            self.callback(event.src_path)

def start_watching(target_folder, callback):
    event_handler = FileWatcher(callback)
    observer = Observer()
    observer.schedule(event_handler, target_folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()