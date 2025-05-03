import os
from pathlib import Path

class FileScanner:
    def __init__(self, target_path):
        self.target_path = Path(target_path)
        
    def get_files(self):
        files = []
        for entry in self.target_path.rglob("*"):
            if entry.is_file():
                files.append({
                    "path": str(entry),  # Chemin complet du fichier
                    "name": entry.name,
                    "type": entry.suffix.lower(),
                    "size": entry.stat().st_size
                })
        return files