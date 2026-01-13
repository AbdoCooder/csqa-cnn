
# Model Architecture

# The Base
>We use MobileNetV2 pre-trained on ImageNet to extract powerful features (shapes, textures, colors).

Since we are using MobileNetV2, we won't be building a neural network from scratch (which takes forever to train).
- Instead, we will use __*Transfer Learning*__. We are going to download a version of MobileNetV2 that has already been trained on millions of images (ImageNet).

## MobileNetV2 function
```py
keras.applications.MobileNetV2(
  input_shape=None,
  alpha=1.0,
  include_top=True,
  weights="imagenet",
  input_tensor=None,
  pooling=None,
  classes=1000,
  classifier_activation="softmax",
  name=None,
)
```

# The Cut
### We set include_top=False to remove the original layer that classifies things like toasters and dogs...

Why we need to set include_top to False for our specific "Fresh vs. Rotten" project?
> The "top" refers to that final fully-connected layer responsible for making the specific predictions.

Here is why we set it to False for your project:

- Original Top: The standard MobileNetV2 is trained on ImageNet, so its top layer has 1,000 outputs (one for "goldfish", one for "toaster", one for "golden retriever", etc.).

- Our Problem: We don't care about toasters; we only care about Fresh and Rotten fruit.

So, we chop off the original head (`include_top=False`) and stick on a new one that fits our specific needs.

# The Activation

To make these 2 neurons output a probability (e.g., 85% Fresh), we use the Softmax activation function (__AI BASED DECISION__ No idea why!).

### NOTE: I included a step to "freeze" the base model (base_model.trainable = False). This ensures we don't accidentally ruin the pre-trained "knowledge" while training our new layer.

```py
# 1. Load the MobileNetV2 base model (without the top layer)
base_model = tf.keras.applications.MobileNetV2(
  input_shape=(224, 224, 3),
  include_top=False
)

# 2. Freeze the base model (so we don't destroy pre-learned patterns)
base_model.trainable = False

# 3. Build the final model
model = tf.keras.Sequential([
  base_model,
  tf.keras.layers.GlobalAveragePooling2D(),
  tf.keras.layers.Dense(2, activation='softmax') # 2 neurons for Fresh/Rotten
])

# 4. Check the structure
model.summary()
```

## tf.keras.Sequential
Think of `tf.keras.Sequential` as an assembly line or a relay race. The data flows through one layer, gets transformed, and is immediately handed to the next.

Here is what is happening at each station of the assembly line:

### 1. `base_model` (The Expert Observer)

* **What it does:** This is the pre-trained MobileNetV2. It looks at the image and creates a complex "feature map."
* **Analogy:** Imagine an expert who looks at a fruit and makes detailed notes: "I see a curved shape in the top left," "I see a brown texture in the center," "I see a stem."
* **Output:** It outputs a 3D block of data. Think of this as a stack of 1,280 different maps of the image, identifying where different features are.

### 2. `GlobalAveragePooling2D` (The Summarizer)

* **What it does:** This layer simplifies the complex 3D data into a single 1D list.
* **How:** It looks at each of the 1,280 feature maps and calculates the **average** value.
* **Why:** We don't care *where* the rot is (top-left or bottom-right); we just care *if* it is there.
* **Output:** A single list of 1,280 numbers (e.g., "Rotten texture score: 0.9", "Fresh skin score: 0.1").

### 3. `Dense(2, ...)` (The Decision Maker)

* **What it does:** This layer looks at that summary list of 1,280 numbers and makes the final call.
* **How:** It uses learned weights to weigh the evidence. For example, if the "brown texture" score is high, it pushes the final answer toward "Rotten."
* **Output:** 2 numbers (probabilities for Fresh and Rotten).

> So, `Sequential` just wraps these three up so you can treat them as one single unit.

## Output
```
Model: "sequential_2"
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Layer (type)                    ┃ Output Shape           ┃       Param # ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ mobilenetv2_1.00_224            │ (None, 7, 7, 1280)     │     2,257,984 │
│ (Functional)                    │                        │               │
├─────────────────────────────────┼────────────────────────┼───────────────┤
│ global_average_pooling2d_1      │ (None, 1280)           │             0 │
│ (GlobalAveragePooling2D)        │                        │               │
├─────────────────────────────────┼────────────────────────┼───────────────┤
│ dense_2 (Dense)                 │ (None, 2)              │         2,562 │
└─────────────────────────────────┴────────────────────────┴───────────────┘
 Total params: 2,260,546 (8.62 MB)
 Trainable params: 2,562 (10.01 KB)
 Non-trainable params: 2,257,984 (8.61 MB)
```

## Breakdown

**mobilenetv2_1.00_224 (The Pre-trained Eye):**
- This is the massive chunk of the model we downloaded.
- Param # (2,257,984): It contains over 2 million parameters (weights) that already know how to recognize shapes, edges, and textures from the ImageNet dataset.
- Note: See how these are listed as Non-trainable params at the bottom? That is because we "froze" them. We are using this strictly as a feature extractor.

**global_average_pooling2d (The Connector):**
- The MobileNet base outputs a complex 3D block of data (7 × 7 × 1280).
- This layer squashes that block down into a single flat vector of 1,280 numbers. It summarizes what the "Eye" saw.

**dense (The Decision Maker):**
- This is the only layer we actually built from scratch!
- Output Shape (None, 2): These are your two neurons for Fresh and Rotten.
- Trainable params (2,562): This is the only part of the model that will learn during training. Because we only have to update ~2,500 numbers instead of 2 million, your training will be incredibly fast.

# Loss Function
