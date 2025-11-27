# Machine Learning Pipeline - Vegetable Image Classification

## GitHub Repository

**Repository URL:** https://github.com/MariamIssah/mlp_summative.git

## Project Description

This project implements a complete end-to-end Machine Learning pipeline for vegetable image classification using deep learning. The system classifies images of 15 different vegetable types using a Convolutional Neural Network (CNN) built with TensorFlow and Keras. The solution includes data preprocessing, model training, evaluation, API deployment, and a web-based user interface for predictions and model retraining.

The pipeline demonstrates the full ML lifecycle from data acquisition through deployment, including model retraining capabilities, performance monitoring, and load testing. The system is containerized using Docker and can be deployed to cloud platforms for production use.

## Video Demo

**YouTube Video Link:** https://youtu.be/8dplIxMLBFI

The video demonstration covers:

- Prediction process with confidence scores
- Model retraining workflow
- Data visualization features
- API endpoints and UI functionality

## Deployment URLs

### Live Deployments

1. **Streamlit UI (Streamlit Cloud)**: https://mariamissah-mlp-summative-streamlit-app-xb22ep.streamlit.app/

   - ✅ Fully functional web interface
   - ✅ Connected to Render API for accurate predictions
   - ✅ All features available: Predict, Retrain, Visualizations

2. **Render API (Recommended - Most Accurate)**: https://mlp-summative-2.onrender.com

   - ✅ Fully functional with high-accuracy predictions
   - ✅ Model loaded and working correctly
   - 📖 API Documentation: https://mlp-summative-2.onrender.com/docs
   - ✅ Best option for production predictions

3. **Railway API**: https://mlpsummative-production.up.railway.app
   - ⚠️ Functional but has resource limitations
   - ⚠️ Retraining endpoint may timeout/crash due to free tier limits
   - 📖 API Documentation: https://mlpsummative-production.up.railway.app/docs

### Local Development

The Streamlit UI can also be run locally:

- Run locally: `streamlit run streamlit_app.py`
- The UI is configured to use the **Render API** by default for accurate predictions

**Note:** For full functionality including retraining, run the API locally using `uvicorn api.app:app --host 0.0.0.0 --port 8000`. Retraining works perfectly locally but has limitations on cloud platforms due to storage and time constraints.

## Features

### Core Functionality

- Image classification for 15 vegetable classes (Bean, Bitter Gourd, Bottle Gourd, Brinjal, Broccoli, Cabbage, Capsicum, Carrot, Cauliflower, Cucumber, Papaya, Potato, Pumpkin, Radish, Tomato)
- Prediction with confidence scores and probability distributions
- Model retraining with new data
- Real-time model status monitoring
- Data visualization and feature analysis

### Technical Components

- Deep learning model using CNN architecture
- RESTful API built with FastAPI
- Interactive web UI using Streamlit
- Docker containerization
- Load testing with Locust
- Comprehensive model evaluation metrics

## Project Structure

```
mlp_summative/
│
├── README.md
│
├── notebook/
│   └── mlp_summative.ipynb
│
├── src/
│   ├── preprocessing.py
│   ├── model.py
│   ├── prediction.py
│   └── retrain.py
│
├── api/
│   └── app.py
│
├── data/
│   ├── train/
│   ├── validation/
│   └── test/
│
├── models/
│   ├── best_model.h5
│   ├── final_vegetable_model.h5
│   └── class_indices.json
│
├── streamlit_app.py
├── locustfile.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Git (for cloning the repository)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd mlp_summative
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure the data directory structure is in place:

   - `data/train/` - Full training images organized by class (used locally)
   - `data/validation/` - Full validation images organized by class (used locally)
   - `data/train_min/` - Lightweight subset for cloud retraining demos
   - `data/validation_min/` - Lightweight subset for cloud retraining demos
   - `data/test/` - Test images organized by class

   Use `python scripts/create_min_dataset.py --train-count 40 --val-count 12` to regenerate the minimal subset if needed.

4. Ensure model files are present in the `models/` directory:
   - `best_model.h5` - Trained model file
   - `class_indices.json` - Class mapping file

### Running the Application

#### Option 1: Using Docker Compose (Recommended)

1. Build and start the containers:

```bash
docker-compose build
docker-compose up
```

2. The API will be available at `http://localhost:8000`
3. Access the API documentation at `http://localhost:8000/docs`

#### Option 2: Running Locally

1. Start the FastAPI server:

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

2. In a separate terminal, start the Streamlit UI:

```bash
streamlit run streamlit_app.py
```

3. Access the Streamlit interface at `http://localhost:8501`

### Render Deployment Notes

- Set the environment variable `DATA_VARIANT=mini` on the Render service to force the API to use the lightweight dataset.
- Commit and push the `data/train_min` and `data/validation_min` folders (already included in this repository) before deploying; without them the `/retrain` endpoint will raise `No such file or directory: 'data/train'`.
- Ensure `PYTHONPATH` is set to `/app` and the start command is `uvicorn api.app:app --host 0.0.0.0 --port 8000`.
- The Docker build excludes the large `data/train` and `data/validation` folders to keep the image within Render limits. The minimal subset is copied into the image automatically.

### Railway Deployment Notes

- **Deployed URL:** https://mlpsummative-production.up.railway.app
- Railway automatically injects a `PORT` environment variable; the Dockerfile uses a start script that properly handles this.
- Add `DATA_VARIANT=mini` (or `auto`) in Project Settings → Variables so that retraining uses the bundled minimal dataset.
- **Deployed Model:** The model is trained during Docker build using a lightweight architecture optimized for Railway's free tier. The model provides good accuracy for predictions while staying within memory limits.
- **Retraining Limitations:** The `/retrain` endpoint **will crash or timeout** on Railway's free tier due to:
  - **Storage limits**: Insufficient disk space for model training
  - **Time limits**: Request timeout (typically 60-120 seconds) - model training takes longer
  - **Memory constraints**: OOM (Out of Memory) errors during training
  - **Solution**: Retraining works perfectly locally. For cloud deployment, use the pre-trained model included in the Docker image. Full retraining functionality is demonstrated and tested locally.
- **Model Loading:** The model loads automatically during Docker build. If you see a 503 error ("Model not loaded"), check Railway logs for model loading errors.
- Railway health checks issue `HEAD /` and `GET /` requests. The service will start and remain running even if the model is still loading in the background.
- Test your deployment at `https://mlpsummative-production.up.railway.app/docs` once the service is running.

### Render Deployment Notes

- **Deployed URL:** https://mlp-summative-2.onrender.com
- **Status:** ✅ **Working with accurate predictions**
- Render deployment uses the full trained model and provides high-accuracy predictions (99%+ confidence).
- The Streamlit UI is configured to use the Render API by default for accurate predictions.
- Set the environment variable `DATA_VARIANT=mini` on the Render service to force the API to use the lightweight dataset for retraining.
- Ensure `PYTHONPATH` is set to `/app` and the start command is `uvicorn api.app:app --host 0.0.0.0 --port 8000`.

### API Endpoints

- `GET /` - Health check endpoint
- `POST /predict` - Predict vegetable class from uploaded image
- `POST /retrain` - Retrain the model with new images
- `GET /docs` - Interactive API documentation (Swagger UI)

### Using the Streamlit Interface

1. Navigate to the Streamlit application URL
2. Use the sidebar to access different pages:
   - **Home**: View model status and information
   - **Predict**: Upload an image and get predictions with confidence scores
   - **Retrain**: Upload multiple images to retrain the model
   - **Visualizations**: Explore dataset features and insights

## Model Information

### Architecture

The model uses a Convolutional Neural Network (CNN) with the following architecture:

- Input layer: 224x224x3 RGB images
- Convolutional layers with MaxPooling
- Dense layers with Dropout regularization
- Output layer: 15 classes with softmax activation

### Training Details

- Optimizer: Adam
- Loss function: Categorical crossentropy
- Metrics: Accuracy
- Data augmentation: Rotation, zoom, horizontal flip
- Early stopping and model checkpointing implemented

### Model Files

- `best_model.h5`: Best model saved during training (HDF5 format)
- `final_vegetable_model.h5`: Final trained model
- `class_indices.json`: Mapping of class names to indices

## Load Testing Results

Load testing was performed using Locust to simulate flood requests and measure system performance under different load conditions. Tests were conducted with varying numbers of concurrent users and Docker container configurations.

### Test Configuration

Load tests were executed using the following scenarios:

- Light load: 10 concurrent users
- Medium load: 50 concurrent users
- Heavy load: 100 concurrent users
- Stress test: 200 concurrent users

### Results Summary

Load testing was performed with the API running in Docker containers. The following table summarizes the key performance metrics:

| Container Count | Users | RPS | Median (ms) | 95th %ile (ms) | 99th %ile (ms) | Max (ms) | Failures |
| --------------- | ----- | --- | ----------- | -------------- | -------------- | -------- | -------- |
| 1               | 10    | 5.4 | 240         | 610            | 730            | 926      | 0        |
| 1               | 50    | 7.5 | 4400        | 11000          | 13000          | 16165    | 0        |
| 1               | 100   | 7.1 | 11000       | 26000          | 30000          | 33693    | 0        |
| 3               | 10    | -   | -           | -              | -              | -        | -        |
| 3               | 50    | -   | -           | -              | -              | -        | -        |
| 3               | 100   | -   | -           | -              | -              | -        | -        |
| 5               | 10    | -   | -           | -              | -              | -        | -        |
| 5               | 50    | -   | -           | -              | -              | -        | -        |
| 5               | 100   | -   | -           | -              | -              | -        | -        |

_Note: Response times may be higher than expected due to retraining requests being included in aggregated statistics. Retraining operations take significantly longer (30-90 seconds) than prediction requests (typically 200-700ms)._

### Key Findings

[Add analysis of results here, for example:]

- Single container performance: [Describe performance with 1 container]
- Scaling benefits: [Describe how performance improves with multiple containers]
- Bottlenecks identified: [Any performance issues found]
- Recommended configuration: [Optimal container count for production]

### Test Execution

To reproduce these results:

1. Start the API with the desired number of containers
2. Run Locust tests using the provided locustfile.py
3. Record metrics from the Locust web interface or HTML reports
4. Repeat for different container configurations

Example commands:

```bash
# Test with 50 users for 60 seconds
locust --headless -u 50 -r 5 -t 60s --host http://localhost:8000 --html results/50_users_1_container.html

# Test with 100 users
locust --headless -u 100 -r 10 -t 120s --host http://localhost:8000 --html results/100_users_1_container.html
```

Detailed load testing documentation and scripts are available in `LOAD_TESTING.md`.

### Running Load Tests

To run load tests locally:

1. Ensure the API is running
2. Install Locust if not already installed:

```bash
pip install locust
```

3. Run Locust with the provided configuration:

```bash
locust --host http://localhost:8000
```

4. Access the Locust web interface at `http://localhost:8089`

5. For automated testing, use the provided scripts:
   - Windows: `.\run_load_tests.ps1`
   - Linux/Mac: `./run_load_tests.sh`

Detailed load testing documentation is available in `LOAD_TESTING.md`.

## Model Evaluation

The model was evaluated using multiple metrics as demonstrated in the Jupyter notebook (`notebook/mlp_summative.ipynb`):

### Evaluation Metrics Implemented

✅ **Accuracy**: Overall classification accuracy (tracked during training and validation)

- Final training accuracy: ~93.4%
- Final validation accuracy: ~97.0%

✅ **Precision**: Per-class precision scores calculated using `sklearn.metrics.classification_report`

- Average precision across all classes: ~0.97

✅ **Recall**: Per-class recall scores calculated using `sklearn.metrics.classification_report`

- Average recall across all classes: ~0.97

✅ **F1-Score**: Harmonic mean of precision and recall

- Average F1-score across all classes: ~0.97

✅ **Confusion Matrix**: Detailed classification performance matrix visualized using `ConfusionMatrixDisplay`

- Shows per-class classification performance
- Visualized with all 15 vegetable classes

### Notebook Contents

The notebook (`notebook/mlp_summative.ipynb`) contains:

- Complete data preprocessing pipeline
- Model training with optimization techniques:
  - EarlyStopping callback
  - ModelCheckpoint callback
  - Data augmentation (rotation, zoom, horizontal flip)
  - Transfer learning with MobileNetV2
- Comprehensive evaluation metrics (all 4+ required metrics)
- Feature visualizations and interpretations
- Single prediction demonstrations

## Retraining Process

The system supports model retraining with the following workflow:

1. **Data Upload**: Users can upload multiple vegetable images through the Streamlit interface or API
2. **Data Preprocessing**: Uploaded images are processed and prepared for training
3. **Model Retraining**: The model is retrained from scratch using the existing training data combined with newly uploaded images
4. **Model Evaluation**: Training metrics and performance analysis are displayed
5. **Model Deployment**: The retrained model is automatically saved and becomes available for predictions

The retraining process includes:

- Training progress visualization
- Accuracy and loss metrics tracking
- Performance analysis and recommendations
- Automatic model versioning

## Data Visualizations

The application includes three key feature visualizations:

1. **Image Brightness Distribution**: Analysis of brightness levels across vegetable images
2. **Aspect Ratio Distribution**: Width-to-height ratio patterns in the dataset
3. **Edge Density Distribution**: Texture complexity analysis through edge detection

These visualizations help understand dataset characteristics and model decision-making patterns.

## Technologies Used

- **Deep Learning**: TensorFlow, Keras
- **API Framework**: FastAPI
- **Web Interface**: Streamlit
- **Image Processing**: PIL (Pillow), NumPy
- **Data Analysis**: Pandas, Matplotlib
- **Load Testing**: Locust
- **Containerization**: Docker, Docker Compose
- **Python Version**: 3.11

## Requirements

All required dependencies are listed in `requirements.txt`. Key packages include:

- fastapi
- uvicorn
- tensorflow
- keras
- streamlit
- pillow
- numpy
- pandas
- matplotlib
- locust

## Deployment Challenges and Solutions

### Challenges Encountered

During the deployment process, several significant challenges were encountered:

#### 1. **Model File Size and Git LFS Issues**

- **Problem**: The trained model file (`best_model.h5`) is 134MB, exceeding GitHub's file size limits
- **Solution**: Implemented Git LFS (Large File Storage) to track model files. However, this caused issues with cloud deployments where LFS files weren't always pulled correctly
- **Workaround**: Created a lightweight model training script (`scripts/train_small_model_for_railway.py`) that trains a smaller model during Docker build

#### 2. **Memory Constraints on Free Tier Platforms**

- **Problem**: Railway and Render free tiers have strict memory limits (typically 512MB-1GB)
- **Impact**:
  - Model training during Docker build would fail with "Out of Memory" errors
  - Large model files couldn't be loaded
  - Training scripts with full datasets would crash
- **Solution**:
  - Optimized model architecture to use less memory
  - Reduced batch sizes (32 → 8)
  - Created minimal dataset subsets (`data/train_min`, `data/validation_min`)
  - Implemented fallback dummy model creation if training fails

#### 3. **Retraining Endpoint Timeout Issues**

- **Problem**: The `/retrain` endpoint consistently crashes or times out on cloud platforms
- **Root Causes**:
  - **Storage limits**: Insufficient disk space for saving trained models
  - **Time limits**: Cloud platforms (Railway/Render) have request timeout limits (60-120 seconds)
  - **Memory limits**: Model training requires significant RAM, causing OOM errors
  - **CPU constraints**: Free tier CPU resources are limited, making training extremely slow
- **Current Status**:
  - ✅ **Works perfectly locally** - Full retraining functionality with high accuracy
  - ❌ **Fails on cloud platforms** - Timeout or crash due to resource constraints
- **Solution**:
  - Retraining is demonstrated and tested locally
  - Cloud deployment focuses on prediction capabilities using pre-trained models
  - For production retraining, use local environment or upgrade to paid cloud tiers

#### 4. **Model Loading and Path Issues**

- **Problem**: Model file paths differed between local, Docker, and cloud environments
- **Solution**: Implemented multi-path detection that checks:
  - `/app/models/best_model.h5` (Docker/Railway)
  - `models/best_model.h5` (local/Render)
  - Relative paths as fallback
- **Result**: Model loading now works reliably across all environments

#### 5. **Streamlit Cloud Deployment Issues**

- **Problem**: Streamlit Cloud tried to install all dependencies including TensorFlow (very large)
- **Solution**: Created separate `requirements.txt` (minimal for Streamlit) and `requirements-api.txt` (full dependencies for API)
- **Additional Issue**: `packages.txt` had comments that were interpreted as package names
- **Solution**: Made `packages.txt` empty (no system packages needed)

#### 6. **Health Check and Startup Issues**

- **Problem**: Railway health checks would fail if model loading blocked startup
- **Solution**: Implemented background model loading with threading, allowing health checks to respond immediately while model loads in the background

### Current Deployment Status

- ✅ **Render API**: Fully functional with accurate predictions (https://mlp-summative-2.onrender.com)
- ⚠️ **Railway API**: Deployed but retraining has limitations (https://mlpsummative-production.up.railway.app)
- ✅ **Streamlit UI**: Configured to use Render API for accurate predictions
- ✅ **Local Environment**: All features work perfectly including full retraining

### Recommendations

1. **For Production Retraining**: Use local environment or upgrade to paid cloud tiers with more resources
2. **For Predictions**: Use Render API (most accurate) or Railway API (functional)
3. **For Development**: Run locally with full dataset for best performance
4. **For Demonstrations**: Use pre-trained models included in Docker images

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 8000 is already allocated, stop the existing process or change the port in the configuration
2. **Model file not found**: Ensure `models/best_model.h5` exists in the models directory
3. **Data directory missing**: Verify that the data directory structure matches the expected format
4. **Docker build fails**: Check that all files are present and Docker has sufficient resources
5. **Retrain endpoint crashes**: This is expected on free tier cloud platforms. Use local environment for retraining.
6. **503 Model not loaded**: Check Railway/Render logs. Model should load during Docker build. If not, check for OOM errors.

### Getting Help

For issues or questions:

1. Check the API documentation at `/docs` endpoint
2. Review the Jupyter notebook for model training details
3. Consult the load testing guide in `LOAD_TESTING.md`
4. For retraining: Use local environment - cloud platforms have resource limitations

## Future Improvements

Potential enhancements for the system:

- Integration with cloud storage for data management
- Automated retraining triggers based on data drift
- Model versioning and A/B testing capabilities
- Enhanced monitoring and logging
- Support for additional vegetable classes
- Real-time prediction streaming

## License

[Add license information if applicable]

## Author

Mariam Issah
Email: m.issah1@alustudent.com
GitHub: [MariamIssah](https://github.com/MariamIssah)

## Acknowledgments

- Dataset: Vegetable Images dataset
- Framework documentation: TensorFlow, FastAPI, Streamlit
- Load testing tool: Locust
