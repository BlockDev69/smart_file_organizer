import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from core.scanner import FileScanner
from core.watcher import start_watching
from core.classifier import FileClassifier
from core.organizer import FileOrganizer
import threading
import os

class DarkTheme:
    BACKGROUND = "#2d2d2d"
    FOREGROUND = "#ffffff"
    ACCENT = "#3498db"
    ENTRY_BG = "#404040"
    TREE_HEADING_BG = "#404040"
    TREE_ROW_BG = "#353535"
    TREE_ALT_ROW_BG = "#3d3d3d"

class FileOrganizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart File Organizer")
        self.geometry("1000x700")
        self.configure(bg=DarkTheme.BACKGROUND)
        
        # Configuration du style
        self.style = ttk.Style()
        self._configure_styles()
        
        # Variables
        self.target_folder = tk.StringVar()
        self.file_list = []
        self.watcher_thread = None
        self.classifier = FileClassifier()
        
        # Création des widgets
        self._create_widgets()
        
    def _configure_styles(self):
        """Configure les styles personnalisés pour l'interface"""
        self.style.theme_use('clam')
        
        # Configuration des couleurs
        self.style.configure(
            "TFrame",
            background=DarkTheme.BACKGROUND
        )
        self.style.configure(
            "TLabel",
            background=DarkTheme.BACKGROUND,
            foreground=DarkTheme.FOREGROUND
        )
        self.style.configure(
            "TButton",
            background=DarkTheme.ACCENT,
            foreground=DarkTheme.FOREGROUND,
            borderwidth=0,
            focuscolor=DarkTheme.ACCENT
        )
        self.style.map(
            "TButton",
            background=[("active", DarkTheme.ACCENT), ("disabled", "#7f8c8d")]
        )
        self.style.configure(
            "TEntry",
            fieldbackground=DarkTheme.ENTRY_BG,
            foreground=DarkTheme.FOREGROUND
        )
        self.style.configure(
            "Header.TLabel",
            font=("Helvetica", 12, "bold"),
            padding=5
        )
        self.style.configure(
            "Treeview.Heading",
            background=DarkTheme.TREE_HEADING_BG,
            foreground=DarkTheme.FOREGROUND,
            relief="flat"
        )
        self.style.configure(
            "Treeview",
            background=DarkTheme.TREE_ROW_BG,
            foreground=DarkTheme.FOREGROUND,
            fieldbackground=DarkTheme.TREE_ROW_BG,
            borderwidth=0
        )
        self.style.map(
            "Treeview",
            background=[("selected", DarkTheme.ACCENT)]
        )

    def _create_widgets(self):
        """Crée et positionne les composants de l'interface"""
        # Conteneur principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Section d'en-tête
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            header_frame,
            text="📁 Smart File Organizer",
            style="Header.TLabel"
        ).pack(side=tk.LEFT)
        
        # Section de sélection de dossier
        folder_frame = ttk.LabelFrame(
            main_frame,
            text=" Dossier Cible ",
            padding=(10, 5))
        folder_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(
            folder_frame,
            textvariable=self.target_folder,
            width=50,
            font=("Helvetica", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            folder_frame,
            text="Parcourir",
            command=self.browse_folder,
            width=10
        ).pack(side=tk.LEFT)
        
        # Section de liste de fichiers
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Name", "Type", "Predicted Category"),
            show="headings",
            selectmode="extended"
        )
        
        # Configuration des colonnes
        self.tree.heading("Name", text="Nom du Fichier", anchor=tk.W)
        self.tree.heading("Type", text="Type", anchor=tk.W)
        self.tree.heading("Predicted Category", text="Catégorie Prédite", anchor=tk.W)
        
        self.tree.column("Name", width=400, anchor=tk.W)
        self.tree.column("Type", width=150, anchor=tk.W)
        self.tree.column("Predicted Category", width=200, anchor=tk.W)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Barre de progression
        self.progress = ttk.Progressbar(
            main_frame,
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=10)
        
        # Contrôles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=15)
        
        self.scan_btn = ttk.Button(
            control_frame,
            text="Scanner le Dossier",
            command=self.start_scan,
            width=15
        )
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.organize_btn = ttk.Button(
            control_frame,
            text="Organiser les Fichiers",
            command=self.organize_files,
            width=15
        )
        self.organize_btn.pack(side=tk.LEFT)
        
        ttk.Button(
            control_frame,
            text="Paramètres",
            command=self.show_settings,
            width=10
        ).pack(side=tk.RIGHT)
        
        # Barre de statut
        self.status_bar = ttk.Label(
            self,
            text="Prêt",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_status(self, message):
        """Met à jour la barre de statut"""
        self.status_bar.config(text=message)
        self.update_idletasks()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder.set(folder)
            self.start_watcher(folder)
            
    def start_scan(self):
        if not self.target_folder.get():
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un dossier cible.")
            return
        
        self._update_status("Scan en cours...")
        self.progress.start()
        self.scan_btn.config(state=tk.DISABLED)
        self.organize_btn.config(state=tk.DISABLED)
        
        scan_thread = threading.Thread(target=self.scan_folder, daemon=True)
        scan_thread.start()
        
    def scan_folder(self):
        """Scanner le dossier et mettre à jour la liste des fichiers"""
        if not self.target_folder.get():
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un dossier cible.")
            return

        scanner = FileScanner(self.target_folder.get())
        files = scanner.get_files()
        
        # Prédire la catégorie pour chaque fichier
        self.file_list = []
        for file in files:
            category = self.classifier.predict_category(file["name"])
            self.file_list.append({
                "path": file["path"],  # Ajouter le chemin complet
                "name": file["name"],
                "type": file["type"],
                "category": category
            })
        
        self.update_file_list()
        self.progress.stop()
        self._update_status("Prêt")
        self.scan_btn.config(state=tk.NORMAL)
        self.organize_btn.config(state=tk.NORMAL)
        
    def update_file_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for file in self.file_list:
            self.tree.insert("", tk.END, values=(file["name"], file["type"], file["category"]))
            
    def start_watcher(self, target_folder):
        if self.watcher_thread and self.watcher_thread.is_alive():
            return
        
        self.watcher_thread = threading.Thread(
            target=start_watching,
            args=(target_folder, self.handle_new_file),
            daemon=True
        )
        self.watcher_thread.start()
        
    def handle_new_file(self, file_path):
        """Appelé lorsqu'un nouveau fichier est détecté"""
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1]
        category = self.classifier.predict_category(file_name)
        
        self.file_list.append({
            "path": file_path,
            "name": file_name,
            "type": file_type,
            "category": category
        })
        self.update_file_list()
        
    def organize_files(self):
        """Déplace les fichiers dans leurs dossiers respectifs"""
        if not self.target_folder.get():
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un dossier cible.")
            return
            
        self._update_status("Organisation en cours...")
        self.progress.config(mode="determinate", maximum=len(self.file_list), value=0)
        self.progress.start()
        self.scan_btn.config(state=tk.DISABLED)
        self.organize_btn.config(state=tk.DISABLED)
        
        success = 0
        errors = 0
        
        # Organiser les fichiers
        for i, file in enumerate(self.file_list):
            result = FileOrganizer.organize_file(
                source_path=file["path"],
                category=file["category"],
                target_root=self.target_folder.get()
            )
            if result:
                success += 1
            else:
                errors += 1
            
            # Mettre à jour la barre de progression
            self.progress["value"] = i + 1
            self.update_idletasks()  # Forcer la mise à jour de l'interface
        
        # Arrêter la barre de progression après l'organisation
        self.progress.stop()
        
        # Rafraîchir la liste des fichiers
        self.start_scan()
        
        # Mettre à jour le statut et réactiver les boutons
        self._update_status("Prêt")
        self.scan_btn.config(state=tk.NORMAL)
        self.organize_btn.config(state=tk.NORMAL)
        
        # Afficher les résultats
        messagebox.showinfo(
            "Résultats",
            f"Organisation terminée !\n\n"
            f"Fichiers déplacés : {success}\n"
            f"Erreurs : {errors}"
        )
        
    def train_model(self):
        """Entraîner le modèle avec des données réelles"""
        try:
            self.classifier.train_model()
            messagebox.showinfo("Succès", "Le modèle a été entraîné avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'entraînement du modèle : {str(e)}")

    def show_settings(self):
        """Affiche la fenêtre des paramètres"""
        settings_window = tk.Toplevel(self)
        settings_window.title("Paramètres")
        settings_window.geometry("400x300")
        
        # Ajouter le contenu des paramètres ici
        ttk.Label(settings_window, text="Options de classification").pack(pady=10)

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()