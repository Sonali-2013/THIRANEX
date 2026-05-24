import pandas as pd
import numpy as np
import re

from scipy.sparse import hstack

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

import matplotlib.pyplot as plt

# =========================
# DATASET
# =========================

data = {

    "email": [

        "Congratulations! You won a free iPhone. Click now!",
        "Urgent! Verify your bank account immediately.",
        "Meeting scheduled tomorrow at 10 AM.",
        "Project report attached for review.",
        "Claim reward now by visiting this link.",
        "Lunch at 1 PM today?",
        "Reset your password immediately.",
        "Amazon order shipped successfully.",
        "Win cash prize now!!!",
        "Team meeting postponed.",

        "Free crypto giveaway click here!",
        "Security alert verify your account now.",
        "Invoice attached for your purchase.",
        "Your package arrives tomorrow.",
        "Click this malicious URL now!"
    ],

    "label": [

        "Phishing",
        "Phishing",
        "Safe",
        "Safe",
        "Phishing",
        "Safe",
        "Phishing",
        "Safe",
        "Phishing",
        "Safe",

        "Phishing",
        "Phishing",
        "Safe",
        "Safe",
        "Phishing"
    ]
}

df = pd.DataFrame(data)

# =========================
# FEATURE EXTRACTION
# =========================

def extract_features(texts):

    features = []

    for text in texts:

        url_count = len(
            re.findall(r'http[s]?://', text)
        )

        keyword_count = len(
            re.findall(
                r'urgent|verify|click|reward|free|cash|password|crypto|alert',
                text.lower()
            )
        )

        exclamation_count = text.count("!")

        uppercase_ratio = (
            sum(1 for c in text if c.isupper())
            / max(len(text), 1)
        )

        features.append([
            url_count,
            keyword_count,
            exclamation_count,
            uppercase_ratio
        ])

    return np.array(features)

# =========================
# SPLIT DATA
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    df['email'],
    df['label'],
    test_size=0.2,
    random_state=42
)

# =========================
# TF-IDF
# =========================

vectorizer = TfidfVectorizer(
    stop_words='english',
    ngram_range=(1, 2),
    max_features=5000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# =========================
# CUSTOM FEATURES
# =========================

X_train_custom = extract_features(X_train)
X_test_custom = extract_features(X_test)

# =========================
# COMBINE FEATURES
# =========================

X_train_final = hstack((
    X_train_tfidf,
    X_train_custom
))

X_test_final = hstack((
    X_test_tfidf,
    X_test_custom
))

# =========================
# MODEL TRAINING
# =========================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train_final, y_train)

# =========================
# PREDICTIONS
# =========================

y_pred = model.predict(X_test_final)

# =========================
# RESULTS
# =========================

accuracy = accuracy_score(y_test, y_pred)

print("=" * 50)
print("PHISHING EMAIL DETECTION RESULTS")
print("=" * 50)

print(f"Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:\n")

print(classification_report(
    y_test,
    y_pred
))

# =========================
# CONFUSION MATRIX
# =========================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")
print(cm)

plt.figure(figsize=(5,5))

plt.imshow(cm)

plt.title("Confusion Matrix")

plt.colorbar()

classes = ["Phishing", "Safe"]

plt.xticks(range(len(classes)), classes)
plt.yticks(range(len(classes)), classes)

plt.xlabel("Predicted")
plt.ylabel("Actual")

for i in range(len(cm)):
    for j in range(len(cm[0])):
        plt.text(
            j,
            i,
            cm[i][j],
            ha='center',
            va='center'
        )

plt.show()

# =========================
# CUSTOM EMAIL TEST
# =========================

print("\nCUSTOM EMAIL TEST")

user_email = input("\nEnter Email Content:\n")

user_tfidf = vectorizer.transform(
    [user_email]
)

user_custom = extract_features(
    [user_email]
)

user_final = hstack((
    user_tfidf,
    user_custom
))

prediction = model.predict(
    user_final
)[0]

confidence = model.predict_proba(
    user_final
).max()

print(f"\nPrediction : {prediction}")
print(f"Confidence : {confidence * 100:.2f}%")