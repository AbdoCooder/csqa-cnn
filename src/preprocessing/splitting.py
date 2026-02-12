"""Module providing a function to Split the data into two Classes for classification"""

import os
import shutil
import random

# Default Values
SOURCE_ROOT = "/home/abenajib/csqa-cnn/data/dates_dataset_ready"
DEST_ROOT = "/home/abenajib/csqa-cnn/data/dates_dataset_final"
TRAIN_SPLIT = 0.8

def split_dataset(source_root : str   = SOURCE_ROOT,
                  dest_root   : str   = DEST_ROOT,
                  train_split : float = TRAIN_SPLIT,
                  save_as_zip : bool  = False) -> None:
    """
    Splits a dataset of images into training and testing sets based on predefined class labels.

    The function creates directories for the training and testing datasets for each class,
    copies the images from the source directory to the respective destination directories,
    and shuffles the images before splitting them into training and testing sets.

    The dataset is split according to the train_split ratio, which determines the proportion
    of images to be used for training versus testing.

    Raises:
      FileNotFoundError: If the source directory for any class does not exist.

    Prints:
      A summary of the number of training and testing images processed for each class,
      as well as a completion message with the final dataset location.

    Usage:
      Call this function after setting the source_root, dest_root, and train_split variables.
    """
    classes = ['Fresh', 'Rotten']

    for split in ['train', 'test']:
        for class_name in classes:
            os.makedirs(os.path.join(dest_root, split, class_name), exist_ok=True)

    print(f"🚀 Splitting dataset from '{source_root}'...")

    for class_name in classes:
        class_dir = os.path.join(source_root, class_name)
        if not os.path.exists(class_dir):
            print(f"⚠️ Warning: Folder '{class_dir}' not found. Skipping.")
            continue

        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        images = [
            f for f in os.listdir(class_dir)
            if f.lower().endswith(valid_extensions)
        ]

        random.shuffle(images)

        split_point = int(len(images) * train_split)
        train_imgs = images[:split_point]
        test_imgs = images[split_point:]

        print(f"   Processing '{class_name}': {len(train_imgs)} Train / {len(test_imgs)} Test")

        for filename in train_imgs:
            src = os.path.join(class_dir, filename)
            dst = os.path.join(dest_root, 'train', class_name, filename)
            shutil.copy2(src, dst)

        for filename in test_imgs:
            src = os.path.join(class_dir, filename)
            dst = os.path.join(dest_root, 'test', class_name, filename)
            shutil.copy2(src, dst)

    print("-" * 30)
    print("✅ Split Complete!")
    print(f"📂 Final Dataset is ready at: {os.path.abspath(dest_root)}")
    if save_as_zip:
        shutil.make_archive('dates_dataset_final', 'zip', 'dates_dataset_final')
        print("✅ Folder zipped successfully!")

if __name__ == "__main__":
    split_dataset()
