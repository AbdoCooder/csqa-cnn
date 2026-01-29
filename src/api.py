"""
This module provides the diffrent API endpoints to
interact with the AI model

You can run the server using `uvicorn src.api:app --reload` from project root
or `uvicorn api:app --reload` from the src/ directory

"""

import sys
from   pathlib    import Path
from   io         import BytesIO
from   fastapi    import FastAPI, UploadFile
from   pydantic   import BaseModel
import numpy      as np
import tensorflow as tf
import keras

SRC_DIR = Path(__file__).resolve(strict=True).parent
MODELS_DIR = SRC_DIR.parent.joinpath('models')
MODEL_NAME = 'mobilenet_dates.keras'
TRAINED_MODEL_PATH = MODELS_DIR.joinpath(MODEL_NAME)
CLASSES = ['Fresh', 'Dry']

class PredictionOut(BaseModel):
    """Model's Output"""
    predicted_class:str
    confidence:float

app = FastAPI()

try:
    model = keras.models.load_model(TRAINED_MODEL_PATH)
    model.summary() # type: ignore
    print("Model loaded successfully!")
except (FileNotFoundError, ValueError, OSError) as e:
    print(f"CRITICAL ERROR: Failed to load the model: {e}")
    sys.exit(1)

@app.post("/upload_and_predict/", response_model=PredictionOut)
def upload_and_predict(file: UploadFile):
    """
    Endpoint to upload an image and get a prediction.

    Args:
        file: The uploaded image file.

    Returns:
        PredictionOut: A dict containing the predicted class (str) and confidence (float).
    """

    img = keras.utils.load_img(BytesIO(file.file.read()), target_size=(224, 224))

    image_array = keras.utils.img_to_array(img)
    image_array = tf.expand_dims(image_array, 0)  # Create a batch dimension

    # Make a prediction
    predictions = model.predict(image_array, verbose=0) # type: ignore
    score = tf.nn.softmax(predictions[0])

    # Get the predicted class and confidence
    predicted_class = CLASSES[np.argmax(score)]
    confidence = float(100 * np.max(score))

    return PredictionOut(predicted_class=predicted_class, confidence=confidence)

@app.get('/')
def hi():
    """
    Simple methode to test that the API is working correctly
    """
    return {'Message' : 'Hello API'}
