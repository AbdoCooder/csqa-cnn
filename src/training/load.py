"""Module for loading and preparing training datasets."""

import keras

TRAIN_PATH = '/content/dates_dataset_final/train'
BATCH_SIZE = 32
IMG_HEIGHT = 224
IMG_WIDTH = 224
VALIDATION_SPLIT = 0.2
SEED = 123

def load_datasets(train_path=TRAIN_PATH,
                  batch_size=BATCH_SIZE,
                  img_height=IMG_HEIGHT,
                  img_width=IMG_WIDTH,
                  validation_split=VALIDATION_SPLIT,
                  seed=SEED
                ):
    """
    Load training and validation datasets from directory.

    Args:
        train_path: Path to training data directory
        batch_size: Batch size for data loading
        img_height: Image height for resizing
        img_width: Image width for resizing
        validation_split: Fraction of data to use for validation
        seed: Random seed for reproducibility

    Returns:
        tuple: (train_ds, val_ds)
    """

    train_ds = keras.preprocessing.image_dataset_from_directory(
        train_path,
        validation_split=validation_split,
        subset="training",
        seed=seed,
        image_size=(img_height, img_width),
        batch_size=batch_size
    )

    val_ds = keras.preprocessing.image_dataset_from_directory(
        train_path,
        validation_split=validation_split,
        subset="validation",
        seed=seed,
        image_size=(img_height, img_width),
        batch_size=batch_size
    )

    return train_ds, val_ds


if __name__ == "__main__":
    train, validation = load_datasets()
