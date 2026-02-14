"""

"""

import matplotlib.pyplot as plt
import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Constants
MIN_OBJECT_AREA = 3000
ZOOMED_IN_THRESHOLD = 0.50
CROP_PADDING = 10
MORPH_KERNEL = (7, 7)
DARK_CROP_THRESHOLD = 20

def show_and_save(img, title="", cmap=None, n='0'):
    plt.figure(figsize=(5, 5))
    if len(img.shape) == 2:
        plt.imshow(img, cmap=cmap or "gray")
    else:
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()
    cv2.imwrite(f"step_{n}.png", img)

def _create_foreground_mask(image: np.ndarray) -> np.ndarray:
    # show_and_save(image, "Original Image", n='0')

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    s_channel = hsv[:, :, 1]
    # show_and_save(s_channel, "HSV - Saturation Channel", cmap="gray", n='HSV')

    blurred = cv2.GaussianBlur(s_channel, (5, 5), 0)
    # show_and_save(blurred, "Blurred S Channel", cmap="gray", n='blur')

    _, mask = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    # show_and_save(mask, "Thresholded Mask", cmap="gray", n='threshold')

    kernel = np.ones(MORPH_KERNEL, np.uint8)
    # show_and_save(kernel * 255, "Morph Kernel", cmap="gray", n='0')

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    # show_and_save(mask, "After MORPH_CLOSE", cmap="gray", n='morph_closex2')

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    # show_and_save(mask, "After morphology (Final Mask)", cmap="gray", n='morph_openx1')

    return mask

def _padded_crop(image: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    h_img, w_img = image.shape[:2]
    y1 = max(0, y - CROP_PADDING)
    y2 = min(h_img, y + h + CROP_PADDING)
    x1 = max(0, x - CROP_PADDING)
    x2 = min(w_img, x + w + CROP_PADDING)
    return image[y1:y2, x1:x2]

def _decode_image(image_bytes: bytes) -> np.ndarray | None:
    nparr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def _is_too_dark(crop: np.ndarray) -> bool:
    """Return True if the crop is mostly black (e.g. a shadow or conveyor edge)."""
    return cv2.mean(crop)[0] < DARK_CROP_THRESHOLD

def detect_and_crop(image_bytes: bytes) -> list:
    image = _decode_image(image_bytes)
    if image is None:
        logger.error("Failed to decode image")
        return []

    mask = _create_foreground_mask(image)

    # Check scene type based on the largest contour
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return []

    largest = max(contours, key=cv2.contourArea)
    coverage = cv2.contourArea(largest) / (image.shape[0] * image.shape[1])

    # Scenario 1: Zoomed in single date
    if coverage > ZOOMED_IN_THRESHOLD:
        logger.info(f"Scene: Zoomed-In (Coverage: {coverage:.2f})")
        x, y, w, h = cv2.boundingRect(largest)
        return [_padded_crop(image, x, y, w, h)]

    # Scenario 2: Conveyor belt (multiple items)
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

if __name__ == '__main__':

    def run_on_local_image(path="/content/image.png"):
        with open(path, "rb") as f:
            image_bytes = f.read()

        print(" Image loaded from:", path)

        crops = detect_and_crop(image_bytes)

        print(f"\n Total crops returned: {len(crops)}")

        # for i, crop in enumerate(crops):
        #     show_and_save(crop, f" Final Crop {i}", n=f"final_crop_{i}")

    run_on_local_image("/home/abenajib/csqa-cnn/docs/LaTex/figures/convoyer/original.png")
