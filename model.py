!pip install opencv-python-headless -q
print("OpenCV ready!")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import cv2
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

print("TensorFlow:", tf.__version__)
print("GPU:", tf.config.list_physical_devices('GPU'))

def apply_clahe(image_path, img_size=224):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab[:,:,0] = clahe.apply(lab[:,:,0])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    img = cv2.resize(img, (img_size, img_size))
    img = img / 255.0
    return img

print(" CLAHE function ready!")

train_df = pd.read_csv('/content/train.csv')
train_df['diagnosis'] = train_df['diagnosis'].astype(str)
train_df['id_code'] = train_df['id_code'] + '.png'

train_val_df, test_df = train_test_split(
    train_df, test_size=0.15, random_state=42,
    stratify=train_df['diagnosis']
)
train_data, val_data = train_test_split(
    train_val_df, test_size=0.176, random_state=42,
    stratify=train_val_df['diagnosis']
)

print("Training samples:  ", len(train_data))
print("Validation samples:", len(val_data))
print("Test samples:      ", len(test_df))

classes = np.array([0, 1, 2, 3, 4])
weights = compute_class_weight(
    class_weight='balanced',
    classes=classes,
    y=train_data['diagnosis'].astype(int)
)
class_weights = dict(zip(range(5), weights))

labels = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
for i, (k, v) in enumerate(class_weights.items()):
    print(f"  Grade {k} ({labels[i]}): {v:.2f}")

IMG_SIZE = 224
BATCH_SIZE = 32
IMAGE_DIR = '/content/train_images'

train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=360,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    brightness_range=[0.7, 1.3],
    channel_shift_range=30,
    shear_range=0.1
)
val_gen = ImageDataGenerator(rescale=1./255)

train_flow = train_gen.flow_from_dataframe(
    train_data, directory=IMAGE_DIR,
    x_col='id_code', y_col='diagnosis',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE, class_mode='categorical'
)
val_flow = val_gen.flow_from_dataframe(
    val_data, directory=IMAGE_DIR,
    x_col='id_code', y_col='diagnosis',
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE, class_mode='categorical'
)
print("Generators ready!")

model = tf.keras.models.load_model(
    '/content/drive/MyDrive/DR_PROJECT/best_dr_model.h5'
)
print(" Model loaded!")

for layer in model.layers[:129]:
    layer.trainable = False
for layer in model.layers[129:]:
    layer.trainable = True

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
print("Model ready for fine tuning!")

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

callbacks = [
    EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
    ModelCheckpoint(
        '/content/drive/MyDrive/DR_PROJECT/best_dr_model_v2.h5',
        save_best_only=True,
        verbose=1
    )
]

print("Starting fine tuning...")
history = model.fit(
    train_flow,
    validation_data=val_flow,
    epochs=15,
    class_weight=class_weights,
    callbacks=callbacks
)
