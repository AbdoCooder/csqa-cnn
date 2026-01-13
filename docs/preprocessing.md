# Preprocessing

To feed our "Fresh vs. Rotten" images into a model, we need to set up a data pipeline. This pipeline will grab images from your folders, resize them to be uniform, and organize them into batches.

We need to define two things to get started:

1. The file paths : Where the images live.
2. The image size : What dimensions the model expects.

In my case the folder path is `/content/fruits-fresh-and-rotten-for-classification/dataset/train` and I will be using __MobileNetV2__ (as suggested in your project document 1), we need to make sure our images match what that model expects.

These models are usually trained on square images of a specific size. If we feed them something different, they will throw an error. The standard standard input size for __MobileNetV2__ is $224 \times 224$ pixels.


# Loading the training data into the model

We will use the function `image_dataset_from_directory()`, which is the standard, efficient way to get images off the disk and into your model in Keras.
```py
# Here is the method declaration from Keras
tf.keras.preprocessing.image_dataset_from_directory(
    directory,
    labels='inferred',
    label_mode='int',
    class_names=None,
    color_mode='rgb',
    batch_size=32,
    image_size=(256, 256),
    shuffle=True,
    seed=None,
    validation_split=None,
    subset=None,
    interpolation='bilinear',
    follow_links=False,
    crop_to_aspect_ratio=False,
    pad_to_aspect_ratio=False,
    data_format=None,
    verbose=True
)
```


### 1. Setting the Rules (Parameters)
```py
train_path = '...'
batch_size = 32
img_height = 224
img_width = 224
```
- `224x224`: As we discussed, MobileNetV2 (the brain we will use later) requires images to be exactly this size.
- `Batch Size 32`: instead of feeding the model one image at a time (too slow) or all 10,000 at once (runs out of memory), we feed them in small groups of 32.


### 2. The Smart Loader
```py
tf.keras.preprocessing.image_dataset_from_directory(...)
```
This single function does a lot of heavy lifting that used to require dozens of lines of code.
1. It __reads the files__: It looks into your folder and automatically finds the images.
2. It __labels them__: It looks at the subfolder names (e.g., "Fresh", "Rotten") and automatically assigns the correct label to each image.
3. It __resizes them__: The image_size=(224, 224) argument ensures every apple or banana is squished or stretched to fit the model's input requirement.


### 3. The "Exam" Prep (Validation Split)
```py
validation_split=0.2
subset="training" # or "validation"
```
This part is crucial for scientific accuracy. We are telling Keras: "Take 20% of the images and hide them."

- `train_ds (80%)`: The model sees these and learns from them.

- `val_ds (20%)`: The model never trains on these. We use them only to quiz the model. If the model gets 100% on the training data but 50% on this validation data, we know it's "cheating" (memorizing) rather than actually learning to recognize rot.
### Checking the Output
```py
class_names = train_ds.class_names
print("Classes found:", class_names)
```
The final line print(class_names) asks Keras to list the categories it found.
```
Found 10901 files belonging to 2 classes.
Using 8721 files for training.
Found 10901 files belonging to 2 classes.
Using 2180 files for validation.
Classes found: ['Fresh', 'Rotten']
```

> That is exactly what we wanted to see! We now have a clean dataset with just two classes: Fresh and Rotten. This matches the project requirement perfectly.
