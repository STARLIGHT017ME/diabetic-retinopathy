"""Convert the trained Keras model to TensorFlow Lite for the Flutter app."""
import tensorflow as tf

MODEL_PATH = '/content/drive/MyDrive/DR_PROJECT/best_dr_model_v2.h5'
TFLITE_OUT = '/content/drive/MyDrive/DR_PROJECT/dr_model.tflite'

model = tf.keras.models.load_model(MODEL_PATH)
tflite_model = tf.lite.TFLiteConverter.from_keras_model(model).convert()
with open(TFLITE_OUT, 'wb') as f:
    f.write(tflite_model)
print(f'Saved {TFLITE_OUT} ({len(tflite_model) / 1024 / 1024:.2f} MB)')