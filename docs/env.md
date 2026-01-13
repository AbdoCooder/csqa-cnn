
# How to Create a Project developed using the Kaggle Datasets a Google Collab envirenement.

After opening a new fresh Collab notebook we need to get the dataset.

## Get the Kaggle API Key

1. Go to Kaggle -> Setting -> Legacy API Credentials.
2. Create Legacy API Key and save the JSON file into your device.
3. Open the file in any text editor you prefer.

## Install the opendatasets

```py
!pip install opendatasets

# Collecting opendatasets
#   Downloading opendatasets-0.1.22-py3-none-any.whl.metadata (9.2 kB)
# Requirement already satisfied: tqdm in /usr/local/lib/python3.12/dist-packages (from opendatasets) (4.67.1)
# Requirement already satisfied: kaggle in /usr/local/lib/python3.12/dist-packages (from opendatasets) (1.7.4.5)
# Requirement already satisfied: click in /usr/local/lib/python3.12/dist-packages (from opendatasets) (8.3.1)
# Requirement already satisfied: bleach in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (6.3.0)
# Requirement already satisfied: certifi>=14.05.14 in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (2026.1.4)
# Requirement already satisfied: charset-normalizer in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (3.4.4)
# Requirement already satisfied: idna in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (3.11)
# Requirement already satisfied: protobuf in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (5.29.5)
# Requirement already satisfied: python-dateutil>=2.5.3 in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (2.9.0.post0)
# Requirement already satisfied: python-slugify in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (8.0.4)
# Requirement already satisfied: requests in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (2.32.4)
# Requirement already satisfied: setuptools>=21.0.0 in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (75.2.0)
# Requirement already satisfied: six>=1.10 in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (1.17.0)
# Requirement already satisfied: text-unidecode in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (1.3)
# Requirement already satisfied: urllib3>=1.15.1 in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (2.5.0)
# Requirement already satisfied: webencodings in /usr/local/lib/python3.12/dist-packages (from kaggle->opendatasets) (0.5.1)
# Downloading opendatasets-0.1.22-py3-none-any.whl (15 kB)
# Installing collected packages: opendatasets
# Successfully installed opendatasets-0.1.22
```

Then use this module to load the dataset from Kaggle as the following.

## Load the dataset using the API Key from earlier

- Copy the username and the Key from the JSON file.

```py
import opendatasets as od
od.download("https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification")

# Please provide your Kaggle credentials to download this dataset. Learn more: http://bit.ly/kaggle-creds
# Your Kaggle username: <USERNAME>
# Your Kaggle Key: ··········
# Dataset URL: https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification
# Downloading fruits-fresh-and-rotten-for-classification.zip to ./fruits-fresh-and-rotten-for-classification
# 100%|██████████| 3.58G/3.58G [00:41<00:00, 91.6MB/s]
```

- Notice in the file explorer that all the Kaggle dataset downloaded successfully.

> You Can start Your Magic now! Good Luck.
