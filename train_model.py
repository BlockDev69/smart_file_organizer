from core.classifier import FileClassifier

if __name__ == "__main__":
    # Entraîner le modèle
    classifier = FileClassifier()
    classifier.train_model()
    print("Modèle entraîné et sauvegardé avec succès!")