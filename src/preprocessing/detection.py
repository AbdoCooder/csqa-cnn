"""Image detection and cropping module for date extraction from API requests."""
import cv2
import numpy as np

def detect_and_crop(image_bytes):
    """
    Optimized for API: Detects dates and returns numpy arrays (crops)
    without saving anything to disk.

    Args:
        image_bytes: Raw image data from the API request.

    Returns:
        list: A list of numpy arrays (images), each representing one crop.
    """
    # 1. Decode Image from RAM
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        print("Error: Could not decode image bytes")
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cropped_images = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area > 3000:
            pad = 10
            y1 = max(0, y - pad)
            y2 = min(img.shape[0], y + h + pad)
            x1 = max(0, x - pad)
            x2 = min(img.shape[1], x + w + pad)
            crop = img[y1:y2, x1:x2]
            cropped_images.append(crop)

    print(f"Processing complete. Found {len(cropped_images)} objects.")
    return cropped_images
