import pandas as pd
import numpy as np
import os
from data_processing import DataProcessing
from autoencoder import AutoEncoder

def main():
    #objects
    data = DataProcessing()
    auto_encoder = AutoEncoder()
    #dataset
    df1 = pd.read_csv(os.path.join('data', 'KDDTrain+.txt'))
    df2 = pd.read_csv(os.path.join('data', 'KDDTest+.txt'))
    #data_processing
    X_train_scaled, X_test_scaled, y_train, y_test, encoder_protocol, encoder_flag, encoder_service, scaler = data.load_and_process(df1, df2)

    X_normal = data.get_normal_traffic(X_train_scaled, y_train)

    #autoencoder
    model = auto_encoder.build_encoder(41)

    history, X_val_ae = auto_encoder.train(model, X_normal)
    threshold = auto_encoder.compute_threshold(model, X_val_ae)
    errors, anomaly_mask= auto_encoder.detect_anomalies(model, X_test_scaled)

if __name__ == '__main__':
    main()
