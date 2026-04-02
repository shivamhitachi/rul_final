#train_dummy_models.py
import os
import joblib
import numpy as np
import tensorflow as tf
from sklearn.ensemble import IsolationForest

print("[INFO] Generating Dummy Models for Triton...")


iso_dir = "model_repository/isolation_forest/1"
lstm_dir = "model_repository/lstm/1"
os.makedirs(iso_dir, exist_ok=True)
os.makedirs(lstm_dir, exist_ok=True)


X_train = np.random.rand(100, 6)
clf = IsolationForest(random_state=42)
clf.fit(X_train)


joblib.dump(clf, f"{iso_dir}/model.joblib")
print("[INFO] Saved Isolation Forest -> model_repository/isolation_forest/1/model.joblib")

seq_len = 6
features = 7

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(seq_len, features)),
    tf.keras.layers.LSTM(16),
    tf.keras.layers.Dense(9)
])


tf.saved_model.save(model, lstm_dir)
print("[INFO] Saved LSTM -> model_repository/lstm/1/saved_model.pb")

print("[SUCCESS] Model Repository is now populated!")