"""
Detection module for isolating date objects from raw camera images.

Supports two scene types:
  - Single zoomed-in photos (one date filling most of the frame)
  - Conveyor belt photos (many small dates scattered across the frame)
"""

import logging
from typing import List

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# --- Configuration ---
MIN_OBJECT_AREA = 3000          # px²  – anything smaller is noise
ZOOMED_IN_THRESHOLD = 0.50      # if one blob covers >50% of the image, it's a close-up
CROP_PADDING = 10               # extra pixels around each detected object
MORPH_KERNEL_SIZE = (7, 7)
DARK_CROP_THRESHOLD = 20        # mean intensity below this → likely a shadow / corner


def _decode_image(image_bytes: bytes) -> np.ndarray | None:
    """Decode raw bytes into a BGR numpy image."""
    buf = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


def _create_foreground_mask(image: np.ndarray) -> np.ndarray:
    """Convert to grayscale, threshold, and clean up into a binary foreground mask."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones(MORPH_KERNEL_SIZE, np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask


def _padded_crop(image: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """Extract a region from *image* with a small padding border."""
    img_h, img_w = image.shape[:2]
    y1 = max(0, y - CROP_PADDING)
    y2 = min(img_h, y + h + CROP_PADDING)
    x1 = max(0, x - CROP_PADDING)
    x2 = min(img_w, x + w + CROP_PADDING)
    return image[y1:y2, x1:x2]


def _is_too_dark(crop: np.ndarray) -> bool:
    """Return True if the crop is mostly black (e.g. a shadow or conveyor edge)."""
    return cv2.mean(crop)[0] < DARK_CROP_THRESHOLD


def detect_and_crop(image_bytes: bytes) -> List[np.ndarray]:
    """
    Detect date objects in a raw image and return them as individual crops.

    Automatically distinguishes between a single zoomed-in photo and a
    conveyor-belt image with many items.

    Args:
        image_bytes: Raw image data (e.g. from an API request body).

    Returns:
        A list of BGR numpy arrays, one per detected date object.
        Returns an empty list if nothing useful is found.
    """
    image = _decode_image(image_bytes)
    if image is None:
        logger.error("Could not decode the incoming image")
        return []

    mask = _create_foreground_mask(image)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        logger.info("No contours found : the image may be blank")
        return []

    # --- Decide which scene type we're looking at ---
    largest = max(contours, key=cv2.contourArea)
    coverage = cv2.contourArea(largest) / (image.shape[0] * image.shape[1])

    if coverage > ZOOMED_IN_THRESHOLD:
        # One object dominates the frame → just tightly crop around it.
        logger.info("Detected a single zoomed-in date (coverage %.0f%%)", coverage * 100)
        x, y, w, h = cv2.boundingRect(largest)
        return [image[y:y + h, x:x + w]]

    # --- Multiple small items (conveyor belt) ---
    logger.info("Detected a conveyor-belt scene – scanning for individual dates")
    crops = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if w * h < MIN_OBJECT_AREA:
            continue  # too small to be a real date

        crop = _padded_crop(image, x, y, w, h)

        if _is_too_dark(crop):
            continue  # likely a shadow or belt edge, not a date

        crops.append(crop)

    logger.info("Found %d valid date object(s)", len(crops))
    return crops
