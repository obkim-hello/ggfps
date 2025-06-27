import os
import random
import shutil
from glob import glob

# Settings
DATA_DIR = 'data/training'
IMG_EXTS = ['.jpg', '.jpeg', '.png']
TRAIN_RATIO = 0.8

# Find all images
images = [f for f in glob(os.path.join(DATA_DIR, '*')) if os.path.splitext(f)[1].lower() in IMG_EXTS]
random.shuffle(images)

split_idx = int(len(images) * TRAIN_RATIO)
train_imgs = images[:split_idx]
val_imgs = images[split_idx:]

# Prepare folders
def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

for split in ['train', 'val']:
    make_dir(os.path.join(DATA_DIR, 'images', split))
    make_dir(os.path.join(DATA_DIR, 'labels', split))

# Copy images and labels
def copy_files(img_list, split):
    for img_path in img_list:
        base = os.path.splitext(os.path.basename(img_path))[0]
        label_path = os.path.join(DATA_DIR, base + '.txt')
        out_img = os.path.join(DATA_DIR, 'images', split, os.path.basename(img_path))
        out_label = os.path.join(DATA_DIR, 'labels', split, base + '.txt')
        shutil.copy2(img_path, out_img)
        if os.path.exists(label_path):
            shutil.copy2(label_path, out_label)

copy_files(train_imgs, 'train')
copy_files(val_imgs, 'val')

print(f"Split {len(images)} images: {len(train_imgs)} train, {len(val_imgs)} val.") 