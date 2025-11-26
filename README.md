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

## Deployment URL

**Cloud Deployment URL:** https://mlpsummative-production.up.railway.app

The application is deployed and accessible at the above URL. The deployment includes:

- FastAPI backend service with prediction and retraining endpoints
- Model serving endpoints
- Health check endpoints

**Streamlit UI Deployment:** The Streamlit UI can be deployed to Streamlit Cloud (recommended) or Railway. See `STREAMLIT_DEPLOYMENT.md` for detailed instructions. The UI automatically connects to the deployed Railway API when running in the cloud.

**Note:** For full functionality including retraining, the API can also be run locally using `uvicorn api.app:app --host 0.0.0.0 --port 8000`.

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
- **Deployed Model:** The model deployed on Railway is a lightweight CNN trained on the mini dataset (`data/train_min`, `data/validation_min`) during Docker image build. This smaller model has lower accuracy than the full model but demonstrates the complete prediction pipeline in production. The full, high-accuracy model (`models/best_model.h5`) is used and evaluated locally in the notebook and Docker environment.
- **Retraining:** The `/retrain` endpoint may timeout (502 error) on Railway's free tier due to resource limits. Full retraining functionality is demonstrated locally. The deployed API focuses on prediction capabilities.
- Railway health checks issue `HEAD /` and `GET /` requests. The service will start and remain running even if the model is still loading in the background.
- Test your deployment at `https://mlpsummative-production.up.railway.app/docs` once the service is running.

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
| 1               | 10    | -   | -           | -              | -              | -        | -        |
| 1               | 50    | -   | -           | -              | -              | -        | -        |
| 1               | 100   | -   | -           | -              | -              | -        | -        |
| 3               | 50    | -   | -           | -              | -              | -        | -        |
| 3               | 100   | -   | -           | -              | -              | -        | -        |
| 5               | 50    | -   | -           | -              | -              | -        | -        |
| 5               | 100   | -   | -           | -              | -              | -        | -        |

_Note: Replace the dashes (-) with actual test results after running Locust tests_

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

The model was evaluated using multiple metrics as demonstrated in the Jupyter notebook:

- Accuracy: Overall classification accuracy
- Precision: Per-class precision scores
- Recall: Per-class recall scores
- F1-Score: Harmonic mean of precision and recall
- Confusion Matrix: Detailed classification performance matrix

The notebook (`notebook/mlp_summative.ipynb`) contains:

- Complete data preprocessing pipeline
- Model training with optimization techniques (EarlyStopping, ModelCheckpoint)
- Comprehensive evaluation metrics
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

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 8000 is already allocated, stop the existing process or change the port in the configuration
2. **Model file not found**: Ensure `models/best_model.h5` exists in the models directory
3. **Data directory missing**: Verify that the data directory structure matches the expected format
4. **Docker build fails**: Check that all files are present and Docker has sufficient resources

### Getting Help

For issues or questions:

1. Check the API documentation at `/docs` endpoint
2. Review the Jupyter notebook for model training details
3. Consult the load testing guide in `LOAD_TESTING.md`

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
