"""Evaluate a trained model on the 550-image held-out test set.
Prints accuracy, the per-class report, and referable-DR (grade >= 2)
sensitivity / specificity / F1. Saves confusion_matrix.png.
"""
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
import seaborn as sns
import matplotlib
matplotlib.use('Agg')

# or best_dr_model.h5
MODEL_PATH = '/content/drive/MyDrive/DR_PROJECT/best_dr_model_v2.h5'
CSV_PATH = '/content/train.csv'
IMAGE_DIR = '/content/train_images'
LABELS = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']

df = pd.read_csv(CSV_PATH)
df['diagnosis'] = df['diagnosis'].astype(str)
df['id_code'] = df['id_code'] + '.png'
_, test_df = train_test_split(
    df, test_size=0.15, random_state=42, stratify=df['diagnosis'])

test_flow = ImageDataGenerator(rescale=1./255).flow_from_dataframe(
    test_df, directory=IMAGE_DIR, x_col='id_code', y_col='diagnosis',
    target_size=(224, 224), batch_size=32, class_mode='categorical', shuffle=False)

model = tf.keras.models.load_model(MODEL_PATH)
loss, acc = model.evaluate(test_flow)
print(f'Test accuracy: {acc * 100:.2f}%   Test loss: {loss:.4f}')

true = test_flow.classes
pred = np.argmax(model.predict(test_flow), axis=1)
print(classification_report(true, pred, target_names=LABELS))

# Referable DR = moderate or worse (grades 2-4), derived from the 5-class predictions
ref_true, ref_pred = true >= 2, pred >= 2
tp = int(np.sum(ref_true & ref_pred))
fn = int(np.sum(ref_true & ~ref_pred))
fp = int(np.sum(~ref_true & ref_pred))
tn = int(np.sum(~ref_true & ~ref_pred))
print(f'Referable DR: sensitivity {tp/(tp+fn)*100:.1f}%, specificity {tn/(tn+fp)*100:.1f}%, '
      f'F1 {2*tp/(2*tp+fp+fn)*100:.1f}%  (TP={tp} FN={fn} FP={fp} TN={tn})')

cm = confusion_matrix(true, pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=LABELS, yticklabels=LABELS)
plt.title('Confusion Matrix')
plt.ylabel('Actual Grade')
plt.xlabel('Predicted Grade')
plt.tight_layout()
plt.savefig('/content/confusion_matrix.png', dpi=150)
print('Saved /content/confusion_matrix.png')
