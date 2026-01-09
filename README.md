# 🍎 Smart Harvest Sorting and Quality Analysis System

An IoT-based intelligent system that automates fruit and vegetable sorting using computer vision, deep learning, and generative AI for real-time quality analysis and reporting.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

The Smart Harvest Sorting and Quality Analysis System revolutionizes agricultural produce handling by combining computer vision, Convolutional Neural Networks (CNN), and generative AI to automatically classify, sort, and analyze the quality of fruits and vegetables in real-time. The system simulates a camera-equipped conveyor belt that continuously monitors products, detects quality issues, and generates comprehensive analysis reports through an AI-powered Quality Manager.

## ✨ Key Features

- **Real-Time Quality Classification**: CNN-based model classifies produce into Fresh or Rotten categories
- **Automated Sorting**: Computer vision system analyzes items on a simulated conveyor belt
- **Anomaly Detection**: Identifies quality defects and irregularities in produce
- **Loss Statistics**: Computes and tracks waste metrics and quality trends
- **AI Quality Manager**: Leverages generative AI to produce detailed analysis reports and insights
- **Custom Dataset**: Purpose-built dataset with two classes (Fresh/Rotten) for accurate classification
- **IoT Integration**: Designed for seamless integration with IoT sensors and actuators

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Conveyor Belt System                      │
│                  (with Camera Simulation)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Computer Vision Processing                      │
│                 (Image Capture & Preprocessing)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                CNN Classification Model                      │
│              (Fresh / Rotten Detection)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Anomaly Detection & Statistics                  │
│           (Loss Computation & Quality Metrics)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                AI Quality Manager                            │
│         (Generative AI for Analysis Reports)                 │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Dataset

The system uses a custom-built dataset specifically designed for agricultural produce quality assessment:

- **Classes**: 2 (Fresh, Rotten)
- **Purpose**: Training CNN model for real-time quality classification
- **Data Collection**: Images captured under various lighting conditions and angles
- **Preprocessing**: Normalized and augmented for robust model performance

## 🧠 CNN Model

The Convolutional Neural Network is trained to distinguish between fresh and rotten produce:

- **Architecture**: Custom CNN designed for binary classification
- **Input**: RGB images of fruits and vegetables
- **Output**: Classification probability (Fresh/Rotten)
- **Training**: Supervised learning on custom dataset
- **Optimization**: Fine-tuned for real-time inference on edge devices

## 🎥 Camera Simulation & Conveyor Belt

The system simulates an industrial conveyor belt setup:

- **Camera Positioning**: Overhead camera for consistent image capture
- **Speed Control**: Adjustable conveyor belt speed for optimal imaging
- **Lighting**: Controlled illumination for reliable detection
- **Trigger Mechanism**: Automated image capture at regular intervals
- **Processing Pipeline**: Real-time frame processing and classification

## 🔍 Anomaly Detection & Loss Statistics

Advanced analytics for quality control and waste management:

- **Defect Detection**: Identifies visual anomalies in produce
- **Quality Scoring**: Assigns quality metrics to each item
- **Loss Tracking**: Monitors percentage of rejected items
- **Trend Analysis**: Tracks quality patterns over time
- **Alert System**: Notifies operators of quality threshold breaches

## 🤖 AI Quality Manager

Generative AI-powered reporting system:

- **Report Generation**: Automated creation of comprehensive quality analysis reports
- **Insights Extraction**: Identifies patterns and trends in quality data
- **Recommendations**: Suggests improvements for quality control processes
- **Natural Language Processing**: Generates human-readable analysis
- **Decision Support**: Provides actionable insights for management

## 🚀 Getting Started

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Required libraries
pip install tensorflow opencv-python numpy pandas matplotlib
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AbdoCooder/csqa-cnn.git
cd csqa-cnn
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the dataset:
```bash
# Instructions for dataset download will be provided
```

### Usage

1. **Train the CNN Model**:
```bash
python train_model.py --dataset ./data --epochs 50
```

2. **Run the Sorting System**:
```bash
python run_sorting.py --camera 0 --model ./models/quality_classifier.h5
```

3. **Generate Quality Reports**:
```bash
python generate_report.py --data ./results --output ./reports
```

## 🛠️ Technology Stack

- **Deep Learning**: TensorFlow/Keras for CNN model
- **Computer Vision**: OpenCV for image processing
- **IoT Integration**: MQTT protocol for sensor communication
- **AI Analytics**: Generative AI (GPT-based) for report generation
- **Data Processing**: NumPy, Pandas for data manipulation
- **Visualization**: Matplotlib, Seaborn for analytics dashboards

## 📁 Project Structure

```
csqa-cnn/
├── data/                    # Dataset directory
│   ├── fresh/              # Fresh produce images
│   └── rotten/             # Rotten produce images
├── models/                  # Trained models
├── src/                     # Source code
│   ├── preprocessing/      # Image preprocessing
│   ├── training/           # Model training scripts
│   ├── inference/          # Real-time classification
│   ├── anomaly/            # Anomaly detection
│   └── reporting/          # AI report generation
├── camera_simulation/       # Conveyor belt simulation
├── results/                 # Classification results and statistics
├── reports/                 # Generated quality reports
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## 🔮 Future Enhancements

- [ ] Multi-class classification for different types of defects
- [ ] Integration with robotic sorting arms
- [ ] Mobile app for remote monitoring
- [ ] Cloud-based analytics dashboard
- [ ] Support for multiple crop types
- [ ] Predictive maintenance for system components
- [ ] Blockchain integration for supply chain tracking

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Abdelkader Benajiba** - *Initial work* - [AbdoCooder](https://github.com/AbdoCooder)

## 🙏 Acknowledgments

- Agricultural research community for domain expertise
- Open-source computer vision and deep learning communities
- IoT and smart farming initiatives

## 📞 Contact

For questions, suggestions, or collaboration opportunities, please open an issue or contact the maintainers.

---

*Built with ❤️ for sustainable and efficient agriculture*
