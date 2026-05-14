from data_processing import *
from autoencoder import *
import tensorflow as tf
from tensorflow.keras import layers
from sklearn.preprocessing import LabelEncoder
import sklearn
import numpy as np


class Classifier:
    def __init__(self):
        pass
        
    def build_classifier(self, input_dim):
        model = tf.keras.Sequential([
            layers.Input(shape = (input_dim,)),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(5, activation='softmax')

        ])

        model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics= ['accuracy'])

        return model
    
    def train(self, model, X_train, y_train):
        label_encoder = LabelEncoder()

        y_train_encoded = label_encoder.fit_transform(y_train)

        X_train_ae, X_val_ae, y_train_ae, y_val_ae = train_test_split(X_train, y_train_encoded, test_size=0.2, random_state=42)

        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor = 'val_loss', patience = 5, restore_best_weights=True)
        ]
        classes = np.unique(y_train_ae)
        weights = sklearn.utils.class_weight.compute_class_weight(
            class_weight='balanced',
            classes=classes,
            y=y_train_ae
        )
        class_weight_dict = dict(zip(classes, weights))
        history = model.fit(X_train_ae, y_train_ae, validation_data = (X_val_ae, y_val_ae), epochs = 100, batch_size = 32, callbacks = callbacks, class_weight = class_weight_dict)

        return history, label_encoder
    
    def predict(self, model, X, label_encoder):
        predictions = model.predict(X)

        class_indices = np.argmax(predictions, axis = 1)

        attack_types = label_encoder.inverse_transform(class_indices)
        confidences = np.max(predictions, axis = 1)

        return attack_types, confidences

