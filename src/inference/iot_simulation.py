"""
A client-side script that acts like a camera on a conveyor belt.
It needs to perform a specific loop indefinitely (or until it runs out of test images)
"""

from pathlib import Path
from time import sleep
import random
import requests


API_URL = 'https://csqa-cnn-api.onrender.com'
IMAGES_PATH = '/home/abdocooder/dev/computer-vision/project/csqa-cnn/data/test'

def test_con():
    """
    Test the api request
    """
    try:
        response = requests.get(API_URL, timeout=60)
        response.raise_for_status()  # Raise exception for bad status codes
        print(response.status_code)
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def images_paths(folder:str) -> list | None:
    """
    Loop through a folder and retreive the path of all the images inside it
    
    :param folder: the folder's path
    """
    folder_path = Path(folder)
    return list(folder_path.rglob("*.jpg")) \
        + list(folder_path.rglob("*.png")) \
        + list(folder_path.rglob("*.jpeg"))

def simulate(img_paths:list):
    """
    Docstring for simulate
    
    :param img_paths: Description
    :type img_paths: list
    """
    print(f"Found {len(img_paths)} images to process")
    try:
        for img in img_paths:
            sleep(2)
            print(f"📸 Capturing: {img.name}...")
            try:
                with open(img, 'rb') as f:
                    res = requests.post(API_URL+'/upload_and_predict', files={"file":f}, timeout=60)
                    if res.status_code == 200:
                        result = res.json()
                        label = result['predicted_class']
                        conf = result['confidence']
                        status_icon = "✅" if label == "Fresh" else "🚨"
                        print(f"--> {status_icon} [{label}] ({conf:.2f}%)")
                    else:
                        print(f"❌ Error {res.status_code}: {res.text}")
            except requests.exceptions.ConnectionError:
                print('Connection Error!')
    except KeyboardInterrupt:
        print("🛑 The simulation stopped by the user!")

if __name__ == '__main__':
    imgs = images_paths(IMAGES_PATH)
    if imgs:
        random.shuffle(imgs)
        simulate(img_paths=imgs)
