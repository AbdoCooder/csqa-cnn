"""FastAPI service for date fruit freshness classification.

Exposes an endpoint that accepts images, detects individual date fruits,
and classifies each as Fresh or Dry using a MobileNet model.
"""
import os
import sys
from pathlib import Path

import cv2
import keras
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, UploadFile
from pydantic import BaseModel
from supabase import Client, create_client
from .preprocessing.detection import detect_and_crop
# LLM ========================================================
from src.reporting.gemini_reporter import GeminiQCReporter
from fastapi.middleware.cors import CORSMiddleware
# ============================================================

load_dotenv()

SRC_DIR = Path(__file__).resolve().parent
MODEL_PATH = SRC_DIR.parent / 'models' / 'mobilenet_dates.keras'
CLASSES = ['Fresh', 'Dry']

# LLM ========================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("CRITICAL ERROR: GEMINI_API_KEY is missing in .env")
    sys.exit(1)
# ============================================================

def require_env(name: str) -> str:
    """Return required environment variable or raise a clear error."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

supabase: Client = create_client(
    require_env("DB_API"),
    require_env("DB_SERVICE_ROLE_KEY")
)

app = FastAPI()

try:
    model = keras.models.load_model(MODEL_PATH)
    print(f"Model loaded: {MODEL_PATH.name}")
except (FileNotFoundError, OSError, ValueError) as e:
    print(f"Failed to load model: {e}")
    sys.exit(1)

# LLM ========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
reporter = GeminiQCReporter(model_name="gemini-2.5-flash")

class ReportIn(BaseModel):
    total: int
    fresh: int
    dry: int

class ReportOut(BaseModel):
    report_md: str

@app.post("/generate_report/", response_model=ReportOut)
def generate_report(payload: ReportIn):
    """
    Generate a French Quality Control report using Gemini LLM.
    """
    report = reporter.generate_report(
        total=payload.total,
        fresh=payload.fresh,
        dry=payload.dry
    )
    return ReportOut(report_md=report)

# ============================================================

class SinglePrediction(BaseModel):
    """Classification result for a single detected date fruit."""

    predicted_class: str
    confidence: float


class BatchPredictionOut(BaseModel):
    """Response containing predictions for all dates found in an image."""

    filename: str
    total_dates_found: int
    results: list[SinglePrediction]


def preprocess_crop(crop):
    """Resize crop to 224x224 and add batch dimension for model input."""
    resized = cv2.resize(crop, (224, 224))
    return tf.expand_dims(resized, 0)


def log_prediction(filename: str, label: str, confidence: float):
    """Insert prediction record into Supabase logs table."""
    try:
        supabase.table("logs").insert({
            "filename": filename,
            "prediction": label,
            "confidence": confidence
        }).execute()
    except (OSError, ValueError) as e:
        print(f"DB log failed: {e}")


@app.post("/upload_and_predict/", response_model=BatchPredictionOut)
async def upload_and_predict(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Detect date fruits in uploaded image and classify each one."""
    image_bytes = await file.read()
    crops = detect_and_crop(image_bytes)

    filename = file.filename or "upload"

    predictions = []
    for i, crop in enumerate(crops):
        preds = model.predict(preprocess_crop(crop), verbose=0)
        score = tf.nn.softmax(preds[0])

        label = CLASSES[np.argmax(score)]
        confidence = float(100 * np.max(score))

        predictions.append(SinglePrediction(predicted_class=label, confidence=confidence))
        background_tasks.add_task(log_prediction, f"{filename}_{i}", label, confidence)

    return BatchPredictionOut(
        filename=filename,
        total_dates_found=len(crops),
        results=predictions
    )


@app.get('/')
def health_check():
    """Return service status and loaded model name."""
    return {'status': 'healthy', 'model': MODEL_PATH.name}
