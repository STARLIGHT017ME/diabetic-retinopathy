"""Stage 1: train a new classification head on a frozen MobileNetV2 base.
Run in Google Colab (T4 GPU) after mounting Google Drive and creating the
folder My Drive/DR_PROJECT. Output: DR_PROJECT/best_dr_model.h5
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

CSV_PATH = '/content/train.csv'
IMAGE_DIR = '/content/train_images'
MODEL_OUT = '/content/drive/MyDrive/DR_PROJECT/best_dr_model.h5'
IMG_SIZE, BATCH_SIZE = 224, 32

# Data splitting: 70% train / 15% validation / 15% test
df = pd.read_csv(CSV_PATH)
df['diagnosis'] = df['diagnosis'].astype(str)
df['id_code'] = df['id_code'] + '.png'
train_val, test_df = train_test_split(
    df, test_size=0.15, random_state=42, stratify=df['diagnosis'])
train_data, val_data = train_test_split(train_val, test_size=0.176, random_state=42,
                                        stratify=train_val['diagnosis'])

# Preprocessing and augmentation (training set only)
train_gen = ImageDataGenerator(rescale=1./255, rotation_range=20, zoom_range=0.2,
                               horizontal_flip=True, vertical_flip=True,
                               brightness_range=[0.8, 1.2])
val_gen = ImageDataGenerator(rescale=1./255)
flow_args = dict(directory=IMAGE_DIR, x_col='id_code', y_col='diagnosis',
                 target_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
                 class_mode='categorical')
train_flow = train_gen.flow_from_dataframe(train_data, **flow_args)
val_flow = val_gen.flow_from_dataframe(val_data, **flow_args)

# Model: frozen MobileNetV2 base + new classification head
base = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3),
                   include_top=False, weights='imagenet')
base.trainable = False
x = GlobalAveragePooling2D()(base.output)
x = Dropout(0.3)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.2)(x)
output = Dense(5, activation='softmax')(x)
model = Model(inputs=base.input, outputs=output)
model.compile(optimizer='adam', loss='categorical_crossentropy',
              metrics=['accuracy'])

callbacks = [EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
             ModelCheckpoint(MODEL_OUT, save_best_only=True, verbose=1)]
model.fit(train_flow, validation_data=val_flow, epochs=20, callbacks=callbacks)
