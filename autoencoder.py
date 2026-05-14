from data_processing import *
import tensorflow as tf
from tensorflow.keras import layers

class AutoEncoder:
    def __init__(self):
        pass

    def build_encoder(self, input_dim: int):

        model = tf.keras.Sequential([
            layers.Input(shape = (input_dim,)),
            layers.Dense(32, activation='relu'),
            layers.Dense(16, activation='relu'),
            layers.Dense(8, activation='relu'),
            layers.Dense(16, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(41, activation='sigmoid')

        ])

        model.compile(optimizer = 'adam', loss = 'mse')

        return model
    
    def train(self, model, X_normal: np.ndarray):
        X_train_ae, X_val_ae = train_test_split(X_normal, test_size=0.2, random_state=42)

        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor = 'val_loss', patience = 5, restore_best_weights=True)
        ]

        history = model.fit(X_train_ae, X_train_ae, validation_data = (X_val_ae, X_val_ae), epochs = 100, batch_size = 32, callbacks = callbacks)

        return history, X_val_ae
    
    def compute_threshold(self, model, X_val_ae):
        reconstructed = model.predict(X_val_ae)
        errors = np.mean(np.square(X_val_ae - reconstructed), axis=1)

        threshold = np.percentile(errors, 95)
        return threshold
    
    def detect_anomalies(self, model, X, threshold):
        reconstructed = model.predict(X)
        errors = np.mean(np.square(X - reconstructed), axis=1)
        anomaly_mask = errors > threshold

        return errors, anomaly_mask





