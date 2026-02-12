"""Module providing a function to reorganize the dataset into Variety_Size_Grade format"""

import os
import shutil
from pathlib import Path

SOURCE_ROOT = "/home/abenajib/csqa-cnn/data/Augmented Date Fruit Dataset"

TARGET_ROOT = "dates_dataset_ready"

FRESH_KEYWORDS = ['Grade-1']
ROTTEN_KEYWORDS = ['Grade-3']

def reorganize_dataset():
    """
    Reorganize dataset by categorizing images into Fresh and Rotten directories.
    
    This function walks through the SOURCE_ROOT directory structure, identifies folders
    based on FRESH_KEYWORDS and ROTTEN_KEYWORDS, and copies image files to corresponding
    destination directories (Fresh or Rotten). Each copied file is renamed with a prefix
    derived from the last 3 parts of its source path (typically Variety_Size_Grade).
    
    Supported image formats: .jpg, .jpeg, .png, .bmp
    
    Side effects:
      - Creates 'Fresh' and 'Rotten' subdirectories in TARGET_ROOT
      - Copies image files to destination directories with renamed filenames
      - Prints reorganization progress and summary statistics to console
    
    Returns:
      None
    """
    fresh_dir = os.path.join(TARGET_ROOT, 'Fresh')
    rotten_dir = os.path.join(TARGET_ROOT, 'Rotten')
    os.makedirs(fresh_dir, exist_ok=True)
    os.makedirs(rotten_dir, exist_ok=True)
    print(f"🚀 Starting reorganization from '{SOURCE_ROOT}'...")

    count_fresh = 0
    count_rotten = 0

    for root, _, files in os.walk(SOURCE_ROOT):
        folder_name = os.path.basename(root)
        destination = None

        if folder_name in FRESH_KEYWORDS:
            destination = fresh_dir
        elif folder_name in ROTTEN_KEYWORDS:
            destination = rotten_dir

        if destination:
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    path_parts = Path(root).parts
                    # Example parts: ('Dataset', 'Aseel', 'Large', 'Grade-1')
                    # We assume the last 3 parts are meaningful (Variety_Size_Grade)
                    prefix = "_".join(path_parts[-3:])
                    new_filename = f"{prefix}_{file}"

                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(destination, new_filename)

                    shutil.copy2(src_path, dst_path)

                    if destination == fresh_dir:
                        count_fresh += 1
                    else:
                        count_rotten += 1

    print("-" * 30)
    print("✅ Reorganization Complete!")
    print(f"📦 Total Fresh (Grade 1): {count_fresh}")
    print(f"📦 Total Rotten (Grade 3): {count_rotten}")
    print(f"📂 Location: {os.path.abspath(TARGET_ROOT)}")

if __name__ == "__main__":
    reorganize_dataset()
