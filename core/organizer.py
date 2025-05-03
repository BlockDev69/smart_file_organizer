import os
import shutil
from pathlib import Path

class FileOrganizer:
    @staticmethod
    def organize_file(source_path: str, category: str, target_root: str):
        """Déplace un fichier dans le dossier de sa catégorie"""
        try:
            dest_dir = Path(target_root) / category
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest_path = dest_dir / Path(source_path).name
            shutil.move(source_path, dest_path)
            return True
        except Exception as e:
            print(f"Erreur lors du déplacement de {source_path}: {str(e)}")
            return False