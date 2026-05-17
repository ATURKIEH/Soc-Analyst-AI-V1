from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import numpy as np
import joblib

class Classifier:
    def __init__(self):
        pass

    def build_classifier(self):
        return RandomForestClassifier(
            n_estimators=200,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )

    def train(self, model, X_train, y_train):
        label_encoder   = LabelEncoder()
        y_encoded       = label_encoder.fit_transform(y_train)

        smote           = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X_train, y_encoded)

        model.fit(X_resampled, y_resampled)

        return model, label_encoder

    def predict(self, model, X, label_encoder):
        predictions  = model.predict_proba(X)
        class_indices = np.argmax(predictions, axis=1)
        attack_types  = label_encoder.inverse_transform(class_indices)
        confidences   = np.max(predictions, axis=1)
        return attack_types, confidences