import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import OneHotEncoder
from scipy.sparse import hstack
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.base import BaseEstimator, TransformerMixin

class ExtensionExtractor(BaseEstimator, TransformerMixin):
    """Extrait l'extension du fichier comme caractéristique."""
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        # Extraire l'extension de chaque fichier
        extensions = [os.path.splitext(x)[1] for x in X]
        return pd.DataFrame(extensions)

class FileClassifier:
    def __init__(self, model_path="models/model.pkl", vectorizer_path="models/vectorizer.pkl", encoder_path="models/encoder.pkl", data_path="data.csv"):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.encoder_path = encoder_path
        self.data_path = data_path
        self.model = None
        self.vectorizer = TfidfVectorizer()  # Vectorizer pour le nom des fichiers
        self.encoder = OneHotEncoder(handle_unknown="ignore")  # Encoder pour les extensions
        
        # Créer le dossier models/ s'il n'existe pas
        os.makedirs("models", exist_ok=True)
        
        # Charger le modèle s'il existe
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path) and os.path.exists(self.encoder_path):
            self.load_model()
        
    def train_model(self):
        """Entraîner le modèle avec des données réelles"""
        # Charger les données
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Le fichier de données {self.data_path} n'existe pas.")
        
        data = pd.read_csv(self.data_path)
        texts = data["file_name"].tolist()
        labels = data["category"].tolist()
        
        # Diviser les données en ensembles d'entraînement et de test
        X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
        
        # Vectoriser le nom du fichier
        X_train_name = self.vectorizer.fit_transform(X_train)
        X_test_name = self.vectorizer.transform(X_test)
        
        # Extraire et encoder les extensions
        X_train_ext = self.encoder.fit_transform(ExtensionExtractor().transform(X_train))
        X_test_ext = self.encoder.transform(ExtensionExtractor().transform(X_test))
        
        # Combiner les caractéristiques
        X_train_vec = hstack([X_train_name, X_train_ext])
        X_test_vec = hstack([X_test_name, X_test_ext])
        
        # Entraînement du modèle
        self.model = MultinomialNB()
        self.model.fit(X_train_vec, y_train)
        
        # Évaluer le modèle
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Précision du modèle : {accuracy:.2f}")
        print("Rapport de classification :")
        print(classification_report(y_test, y_pred))
        
        # Afficher la matrice de confusion
        self.plot_confusion_matrix(y_test, y_pred)
        
        # Sauvegarder le modèle, le vectoriseur et l'encoder
        self.save_model()
        
    def plot_confusion_matrix(self, y_true, y_pred):
        """Afficher la matrice de confusion"""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=self.model.classes_, yticklabels=self.model.classes_)
        plt.xlabel("Prédit")
        plt.ylabel("Réel")
        plt.title("Matrice de Confusion")
        plt.show()
        
    def predict_category(self, file_name):
        """Prédire la catégorie d'un fichier"""
        if not self.model or not self.vectorizer or not self.encoder:
            raise ValueError("Modèle, vectoriseur ou encoder non chargé.")
        
        # Vectoriser le nom du fichier
        X_name = self.vectorizer.transform([file_name])
        # Extraire et encoder l'extension
        X_ext = self.encoder.transform(ExtensionExtractor().transform([file_name]))
        # Combiner les caractéristiques
        X = hstack([X_name, X_ext])
        # Prédire la catégorie
        return self.model.predict(X)[0]
        
    def save_model(self):
        """Sauvegarder le modèle, le vectoriseur et l'encoder"""
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.encoder, self.encoder_path)
        
    def load_model(self):
        """Charger le modèle, le vectoriseur et l'encoder"""
        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.encoder = joblib.load(self.encoder_path)