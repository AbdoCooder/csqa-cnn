"""
    This module contains functions to create and compile a 
    MobileNetV2 model for image classification.
"""

import keras

def create_compiled_model(input_shape=(224, 224, 3), num_classes=2, activation_function='softmax'):
    """
    Creates and compiles a MobileNetV2 model.

    Parameters:
        - input_shape: Shape of the input images.
        - num_classes: Number of output classes.
        - activation_function: The name of the activation function for the output layer

    Returns:
        - Compiled Keras model.
    """

    # Load the MobileNetV2 base model (without the top layer)
    base_model = keras.applications.MobileNetV2(input_shape=input_shape, include_top=False)

    # Freeze the base model
    base_model.trainable = False

    # Build the final model
    model = keras.Sequential([
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(num_classes, activation=activation_function)
    ])

    model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
    )

    print("Model compiled and ready for training!")
    return model

# Example usage
# model = create_compiled_model()
