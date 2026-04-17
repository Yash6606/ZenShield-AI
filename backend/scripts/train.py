import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def train_models():
    # Load data
    data_path = os.path.join(os.path.dirname(__file__), '../data/sample_threats.csv')
    if not os.path.exists(data_path):
        print("Data not found. Run generate_data.py first.")
        return

    df = pd.read_csv(data_path)
    X = df['text']
    y = df['label']

    # Vectorization
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_tfidf = vectorizer.fit_transform(X)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

    # Model 1: Logistic Regression (Baseline)
    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    
    # Model 2: Random Forest
    rf_model = RandomForestClassifier(n_estimators=100)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)

    # Evaluation
    print("--- Logistic Regression Performance ---")
    print(f"Accuracy: {accuracy_score(y_test, lr_preds)}")
    print(classification_report(y_test, lr_preds))

    print("--- Random Forest Performance ---")
    print(f"Accuracy: {accuracy_score(y_test, rf_preds)}")
    print(classification_report(y_test, rf_preds))

    # Save models and vectorizer
    models_dir = os.path.join(os.path.dirname(__file__), '../models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(vectorizer, os.path.join(models_dir, 'tfidf_vectorizer.joblib'))
    joblib.dump(lr_model, os.path.join(models_dir, 'lr_model.joblib'))
    joblib.dump(rf_model, os.path.join(models_dir, 'rf_model.joblib'))
    
    print(f"Models saved to {models_dir}")

if __name__ == "__main__":
    train_models()
