import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# Create models folder if not available
os.makedirs("models", exist_ok=True)


def train_model():
    dataset_path = "data/medirecord_dataset.csv"

    # Read dataset
    df = pd.read_csv(dataset_path)

    print("Dataset loaded successfully.")
    print("Total records:", len(df))

    # Check required columns
    if "medical_note" not in df.columns or "quality" not in df.columns:
        print("Error: Dataset must contain medical_note and quality columns.")
        return

    # Remove empty rows
    df = df.dropna(subset=["medical_note", "quality"])

    # Input and output
    X = df["medical_note"]
    y = df["quality"]

    print("\nQuality label distribution:")
    print(y.value_counts())

    # Split data into training and testing
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Create NLP model pipeline
    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000
        )),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ])

    # Train model
    print("\nTraining model...")
    model.fit(X_train, y_train)

    # Test model
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print("\nModel training completed.")
    print("Accuracy:", accuracy)

    print("\nClassification Report:")
    report = classification_report(y_test, y_pred)
    print(report)

    print("\nConfusion Matrix:")
    matrix = confusion_matrix(y_test, y_pred)
    print(matrix)

    # Save trained model
    model_path = "models/quality_model.pkl"
    joblib.dump(model, model_path)

    print("\nModel saved successfully.")
    print("Saved file:", model_path)

    # Save report as text file
    report_path = "models/model_report.txt"

    with open(report_path, "w") as file:
        file.write("MediRecord SL Model Report\n")
        file.write("==========================\n\n")
        file.write(f"Total records: {len(df)}\n")
        file.write(f"Accuracy: {accuracy}\n\n")
        file.write("Classification Report:\n")
        file.write(report)
        file.write("\nConfusion Matrix:\n")
        file.write(str(matrix))

    print("Model report saved:", report_path)


train_model()