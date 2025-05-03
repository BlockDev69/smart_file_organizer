import os
import pandas as pd

# Dossier racine contenant les fichiers organisés par catégories
root_folder = "C:\DataSet"

data = []
for category in os.listdir(root_folder):
    category_folder = os.path.join(root_folder, category)
    if os.path.isdir(category_folder):
        for file_name in os.listdir(category_folder):
            data.append({
                "file_name": file_name,
                "category": category
            })

# Convertir en DataFrame et sauvegarder en CSV
df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)
print("Dataset créé avec succès!")