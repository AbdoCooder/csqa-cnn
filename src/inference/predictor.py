"""
Fruit Quality Prediction Module
Handles AI inference for date fruit classification (Fresh vs Rotten)
"""

import os
import tensorflow as tf
import numpy as np
import keras

class FruitPredictor:
    """
    AI Vision Engine for Date Fruit Classification.

    Uses MobileNetV2 pre-trained model to classify dates into:
    - Grade 1 (Fresh): Suitable for packaging
    - Grade 3 (Rotten): Rejected/Discarded
    """

    CLASSES = ['Fresh', 'Rotten']
    IMAGE_SIZE = (224, 224)
    # Normalize pixel values to [0, 1] range (standard for deep learning)
    NORMALIZATION_SCALE = 255.0


    def __init__(self, model_path='models/mobilenet_dates.keras'):
        """
        Initialize the predictor with a model path.

        Args:
            model_path (str): Path to the trained .keras model file
        """
        self.model_path = model_path
        self.model = None  # Model loaded lazily on first prediction


    def _build_architecture(self):
        """
        Manually reconstructs MobileNetV2 architecture as fallback.

        This is useful when the model file uses a different Keras version
        and standard loading fails. We rebuild the network and load weights separately.

        Returns:
            keras.Model: Compiled MobileNetV2-based classification model
        """
        print("🔧 Rebuilding MobileNetV2 architecture...")

        base_model = keras.applications.MobileNetV2(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        base_model.trainable = False
        model = keras.Sequential([
            base_model,
            keras.layers.GlobalAveragePooling2D(),
            keras.layers.Dense(2, activation='softmax')
        ])
        return model


    def load_model(self):
        """
        Load the trained model from disk (lazy loading).

        Attempts standard loading first. If that fails (version mismatch),
        falls back to reconstructing architecture and loading weights separately.

        Raises:
            FileNotFoundError: If model file doesn't exist at specified path
        """
        # Check if model file exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"❌ Model file missing at: {self.model_path}")

        try:
            self.model = keras.models.load_model(self.model_path)
            print(f"✅ Model loaded successfully from {self.model_path}")
        except (OSError, AttributeError, ImportError) as e:
            print(f"⚠️ Standard loading failed: {e}")
            print("   Switching to safe-mode: rebuild architecture + load weights...")

            self.model = self._build_architecture()
            self.model.predict(np.zeros((1, 224, 224, 3)))
            self.model.load_weights(self.model_path)
            print("✅ Weights loaded successfully in safe-mode!")

    def predict(self, image_input):
        """
        Run inference on an image to classify fruit quality.

        Args:
            image_input: Either a file path (str) or numpy array
                        - str: Path to image file
                        - ndarray: Image array (will normalize to 0-1 range)

        Returns:
            dict: Prediction result containing:
                - 'label' (str): 'Fresh' or 'Rotten'
                - 'confidence' (float): Probability [0-100]
                - 'is_anomaly' (bool): True if Rotten, False if Fresh
        """
        # Load model on first prediction (lazy loading)
        if not isinstance(self.model, keras.Model):
            self.load_model()
            if not isinstance(self.model, keras.Model):
                raise RuntimeError("Model failed to load properly. Is not a Keras Model instance.")

        # === PREPROCESSING: Convert input to model-ready format ===
        if isinstance(image_input, str):
            # Path-based input: Load image from disk
            img = keras.utils.load_img(image_input, target_size=self.IMAGE_SIZE)
            img_array = keras.utils.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
        else:
            img_array = np.asarray(image_input, dtype=np.float32)
            if len(img_array.shape) == 3:
                img_array = np.expand_dims(img_array, 0)
            elif len(img_array.shape) != 4:
                raise ValueError(f"Expected 3D or 4D array, got shape {img_array.shape}")
        if np.max(img_array) > 1.0:
            img_array = img_array / self.NORMALIZATION_SCALE
        # Ensure float32 type for model
        img_array = np.asarray(img_array, dtype=np.float32)

        # === INFERENCE: Get model predictions ===
        predictions = self.model.predict(img_array)

        # Extract class with highest probability
        predicted_class_idx = np.argmax(predictions[0])
        confidence_score = float(np.max(predictions[0]) * 100)
        predicted_label = self.CLASSES[predicted_class_idx]

        return {
            "label": predicted_label,
            "confidence": confidence_score,
            "is_anomaly": (predicted_label == 'Rotten')
        }
