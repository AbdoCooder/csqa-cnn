"""
A client-side script that acts like a camera on a conveyor belt.
It needs to perform a specific loop indefinitely (or until it runs out of test images)
"""

from time import sleep
from pathlib import Path
import sys
import random
import requests


# Configuration
# API_URL = 'https://csqa-cnn-api.onrender.com'
API_URL = 'http://0.0.0.0:8000' # Uncomment for local testing
IMAGES_PATH = '/home/abenajib/csqa-cnn/data/test'
DELAY = 2

def get_images(folder):
    """Recursively find all images in the folder."""
    p = Path(folder)
    extensions = ['*.jpg', '*.jpeg', '*.png']
    images = []
    for ext in extensions:
        images.extend(p.rglob(ext))
    return images

def simulate_camera(image_list):
    """
    Main loop: Pick an image, send it, print result.
    """
    print(f"🚀 Simulation started. {len(image_list)} images in queue.")
    print("-" * 50)

    try:
        for img_path in image_list:
            filename = img_path.name
            print(f"\n📸 Capture: {filename}")
            try:
                with open(img_path, 'rb') as f:
                    # Send POST request
                    response = requests.post(
                        f"{API_URL}/upload_and_predict/",
                        files={"file": f},
                        timeout=60 # Wait up to 60s (for Render cold starts)
                    )

                if response.status_code == 200:
                    data = response.json()

                    # The new API returns a 'results' list
                    dates_found = data.get('total_dates_found', 0)
                    predictions = data.get('results', [])

                    if dates_found == 0:
                        print("   ⚠️  No dates detected (Empty Belt)")
                    else:
                        print(f"   ⚡ Found {dates_found} objects:")
                        # Loop through each detected date
                        for i, pred in enumerate(predictions, 1):
                            label = pred['predicted_class']
                            conf = pred['confidence']

                            # Visual feedback
                            icon = "✅" if label == "Fresh" else "🚨"
                            print(f"      {i}. {icon} {label} ({conf:.1f}%)")

                else:
                    print(f"❌ Server Error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                print("❌ Connection Failed. Is the API running?")
            except Exception as e:
                print(f"❌ Error: {e}")

            # Wait for the next item
            sleep(DELAY)

    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user.")
        sys.exit(0)

if __name__ == '__main__':
    if not Path(IMAGES_PATH).exists():
        print(f"Error: Folder not found: {IMAGES_PATH}")
        sys.exit(1)

    imgs = get_images(IMAGES_PATH)

    if not imgs:
        print("No images found!")
        sys.exit(1)

    random.shuffle(imgs)
    simulate_camera(imgs)
