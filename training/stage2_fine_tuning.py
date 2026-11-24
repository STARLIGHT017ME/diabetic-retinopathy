"""Stage 2: fine-tune the model. Run after stage1_frozen_base.py.
Input: DR_PROJECT/best_dr_model.h5   Output: DR_PROJECT/best_dr_model_v2.h5
"""
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

CSV_PATH = '/content/train.csv'
IMAGE_DIR = '/content/train_images'
MODEL_IN = '/content/drive/MyDrive/DR_PROJECT/best_dr_model.h5'
MODEL_OUT = '/content/drive/MyDrive/DR_PROJECT/best_dr_model_v2.h5'
IMG_SIZE, BATCH_SIZE = 224, 32

# Same data split as stage 1
df = pd.read_csv(CSV_PATH)
df['diagnosis'] = df['diagnosis'].astype(str)
df['id_code'] = df['id_code'] + '.png'
train_val, test_df = train_test_split(
    df, test_size=0.15, random_state=42, stratify=df['diagnosis'])
train_data, val_data = train_test_split(train_val, test_size=0.176, random_state=42,
                                        stratify=train_val['diagnosis'])

# Class weights to reduce the effect of class imbalance
weights = compute_class_weight('balanced', classes=np.array([0, 1, 2, 3, 4]),
                               y=train_data['diagnosis'].astype(int))
class_weights = dict(zip(range(5), weights))
print('Class weights:', class_weights)

# Stronger augmentation (training set only)
train_gen = ImageDataGenerator(rescale=1./255, rotation_range=360, zoom_range=0.2,
                               horizontal_flip=True, vertical_flip=True,
                               brightness_range=[0.7, 1.3], channel_shift_range=30,
                               shear_range=0.1)
val_gen = ImageDataGenerator(rescale=1./255)
flow_args = dict(directory=IMAGE_DIR, x_col='id_code', y_col='diagnosis',
                 target_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
                 class_mode='categorical')
train_flow = train_gen.flow_from_dataframe(train_data, **flow_args)
val_flow = val_gen.flow_from_dataframe(val_data, **flow_args)

# Load stage 1 model, freeze layers 0-128, unfreeze the last 30 layers
model = tf.keras.models.load_model(MODEL_IN)
for layer in model.layers[:129]:
    layer.trainable = False
for layer in model.layers[129:]:
    layer.trainable = True
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
              loss='categorical_crossentropy', metrics=['accuracy'])

callbacks = [EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
             ModelCheckpoint(MODEL_OUT, save_best_only=True, verbose=1)]
model.fit(train_flow, validation_data=val_flow, epochs=15,
          class_weight=class_weights, callbacks=callbacks)
