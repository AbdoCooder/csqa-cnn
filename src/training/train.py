
"""Module for training models with class weight balancing for imbalanced datasets."""

import numpy as np
from sklearn.utils import class_weight
from training.compile import create_compiled_model

def train_with_class_weights(train_ds, val_ds, epochs=5):
    """Train model with balanced class weights for imbalanced datasets."""

    # Calculate class weights from training data
    train_labels = np.concatenate([y for x, y in train_ds], axis=0)
    class_weights = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_labels),
        y=train_labels
    )
    weights_dict = dict(enumerate(class_weights))
    print(f"⚖️ Calculated Class Weights: {weights_dict}")
    print("(The model will pay more attention to class with higher weight)")

    model = create_compiled_model()

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        class_weight=weights_dict
    )
    print("✅ Model training complete!")

    # Save the model to the Colab disk
    model.save('mobilenet_dates.keras')
    print("✅ Model saved successfully!")

    return model, history
