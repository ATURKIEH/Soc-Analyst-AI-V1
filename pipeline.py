import pandas as pd
import numpy as np
import os
from data_processing import DataProcessing
from autoencoder import AutoEncoder
from classifier import Classifier
from incident_reporter import IncidentReporter

def main():
    #objects
    data = DataProcessing()
    auto_encoder = AutoEncoder()
    classifier = Classifier()
    reporter = IncidentReporter()    
    #data_processing
    X_train_scaled, X_test_scaled, y_train, y_test, encoder_protocol, encoder_flag, encoder_service, scaler = data.load_and_process()

    X_normal = data.get_normal_traffic(X_train_scaled, y_train)

    #autoencoder
    model_autoencoder = auto_encoder.build_encoder(41)

    history, X_val_ae = auto_encoder.train(model_autoencoder, X_normal)
    threshold = auto_encoder.compute_threshold(model_autoencoder, X_val_ae)
    errors, anomaly_mask= auto_encoder.detect_anomalies(model_autoencoder, X_test_scaled, threshold)

    #classifier

    model_classifier = classifier.build_classifier(41)

    history_classifier , label_encoder = classifier.train(model_classifier, X_train_scaled, y_train)
    X_anomalous = X_test_scaled[anomaly_mask]
    attack_types, confidences = classifier.predict(model_classifier, X_anomalous, label_encoder)

    #reporter

    reporter = IncidentReporter()

    results = []
    for i in range(len(X_anomalous)):
        report, risk_score = reporter.generate_report(
            attack_type   = attack_types[i],
            anomaly_score = errors[anomaly_mask][i],
            src_ip        = "unknown",   # no IP in NSL-KDD
            timestamp     = str(pd.Timestamp.now())
        )

        if risk_score >= 80:
            severity = 'Critical'
        elif risk_score >= 60:
            severity = 'High'
        elif risk_score >= 40:
            severity = 'Medium'
        else:
            severity = 'Low'

        results.append({
            "attack_type":   attack_types[i],
            "confidence":    confidences[i],
            "anomaly_score": errors[anomaly_mask][i],
            "risk_score":    risk_score,
            "severity":      severity,
            "report":        report
        })

    return results

if __name__ == '__main__':
    main()
