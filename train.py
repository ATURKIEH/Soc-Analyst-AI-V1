import pandas as pd
import numpy as np
import os
from autoencoder import AutoEncoder
from classifier import Classifier
from data_processing import DataProcessing
from sklearn.metrics import f1_score, classification_report
import pickle as pkl
import joblib
import random
import tensorflow as tf


def main():
    #objects
    data = DataProcessing()
    auto_encoder = AutoEncoder()
    classifier = Classifier()
      
    #data_processing
    X_train_scaled, X_test_scaled, y_train, y_test, encoder_protocol, encoder_flag, encoder_service, scaler = data.load_and_process()

    X_normal = data.get_normal_traffic(X_train_scaled, y_train)

    #autoencoder
    model_autoencoder = auto_encoder.build_encoder(41)

    history, X_val_ae = auto_encoder.train(model_autoencoder, X_normal)
    threshold = auto_encoder.compute_threshold(model_autoencoder, X_val_ae)
    errors, anomaly_mask= auto_encoder.detect_anomalies(model_autoencoder, X_test_scaled, threshold)
    print("======AUTO ENCODER RESULTS======")
    print(f"Detected {len(X_test_scaled[anomaly_mask])} anomalies out of {len(X_test_scaled)} samples.")
    print(f"Threshold: {threshold:.4f}")
    normal_flagged = (y_test[anomaly_mask] == 'normal').sum()
    total_normal   = (y_test == 'normal').sum()
    print(f"Normal samples incorrectly flagged: {normal_flagged}/{total_normal}")
    print(f"Errors: {errors}")

    #classifier

    model_classifier = classifier.build_classifier()

    model_classifier, label_encoder = classifier.train(
                                        model_classifier, X_train_scaled, y_train
                                    )
    X_anomalous = X_test_scaled[anomaly_mask]
    attack_types, confidences = classifier.predict(model_classifier, X_anomalous, label_encoder)
   
    print("======CLASSIFIER RESULTS======")
    print(classification_report(y_test[anomaly_mask], attack_types))
    print(f"F1 Score: {f1_score(y_test[anomaly_mask], attack_types, average='weighted'):.4f}")
    print(f"Accuracy: {(y_test[anomaly_mask] == attack_types).mean():.4f}")
    print("\nTraining label distribution:")
    print(y_train.value_counts())
    print("\nTest anomalies label distribution:")
    print(y_test[anomaly_mask].value_counts())


    os.makedirs('models', exist_ok=True)
    model_autoencoder.save('models/autoencoder_model.keras')
    joblib.dump(model_classifier,  'models/classifier_model.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(label_encoder, 'models/label_encoder.pkl')
    joblib.dump(threshold, 'models/threshold.pkl')
    joblib.dump(encoder_protocol, 'models/encoder_protocol.pkl')
    joblib.dump(encoder_service, 'models/encoder_service.pkl')
    joblib.dump(encoder_flag, 'models/encoder_flag.pkl')


if __name__ == "__main__":
    main()