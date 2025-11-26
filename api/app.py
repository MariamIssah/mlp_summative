from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, Response
from src.prediction import load_trained_model, predict_image
from src.retrain import retrain_model
import os
from typing import List
import traceback

app = FastAPI(title="Vegetable Classification API")

# Log port for Railway debugging
PORT = int(os.getenv("PORT", 8000))
print(f"Starting server on port {PORT}")

@app.on_event("startup")
async def startup_event():
    """Log startup completion for Railway health checks"""
    print("FastAPI application startup complete")

# Determine model path - works for both Docker and Render
if os.path.exists("/app/models/best_model.h5"):
    MODEL_PATH = "/app/models/best_model.h5"  # Docker path
elif os.path.exists("models/best_model.h5"):
    MODEL_PATH = "models/best_model.h5"  # Render/local path
else:
    # Fallback: relative to project root
    MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best_model.h5")

model = None

def load_model(model_path=None):
    """Load or reload the model"""
    global model, MODEL_PATH
    if model_path:
        MODEL_PATH = model_path
    try:
        model = load_trained_model(MODEL_PATH)
        print(f"Model loaded successfully from {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model from {MODEL_PATH}: {e}")
        raise

# Load model at startup
try:
    load_model()
except Exception as e:
    print(f"Failed to load model at startup: {e}")
    model = None

# REAL CLASS LIST (MUST MATCH TRAINING ORDER)
class_names = [
    "Bean", "Bitter_Gourd", "Bottle_Gourd", "Brinjal", "Broccoli",
    "Cabbage", "Capsicum", "Carrot", "Cauliflower", "Cucumber",
    "Papaya", "Potato", "Pumpkin", "Radish", "Tomato"
]

# Paths to training and test data (match your folder structure)
if os.path.exists("/app"):
    BASE_DIR = "/app"  # Docker/Render container
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__)) if os.path.dirname(__file__) else os.getcwd()

DATA_VARIANT = os.getenv("DATA_VARIANT", "auto").lower()

PREFERRED_TRAIN_DIR = os.path.join(BASE_DIR, "data", "train")
FALLBACK_TRAIN_DIR = os.path.join(BASE_DIR, "data", "train_min")
PREFERRED_VAL_DIR = os.path.join(BASE_DIR, "data", "validation")
FALLBACK_VAL_DIR = os.path.join(BASE_DIR, "data", "validation_min")
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "retrain_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def has_training_data(dir_path):
    """Check if directory has any image files."""
    if not os.path.exists(dir_path):
        return False
    for _, _, files in os.walk(dir_path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                return True
    return False


def select_dataset(preferred, fallback, label):
    """Pick the dataset directory to use and report availability."""
    preferred_has = has_training_data(preferred)
    fallback_has = has_training_data(fallback)

    if DATA_VARIANT in ("mini", "minimal", "small", "subset"):
        if fallback_has:
            print(f"DATA_VARIANT={DATA_VARIANT}: using {label} fallback at {fallback}")
            return fallback, True
        print(f"DATA_VARIANT requested minimal {label} dataset but {fallback} is missing.")

    if preferred_has:
        return preferred, True

    if fallback_has:
        print(f"{label.capitalize()} data missing at {preferred}; using fallback {fallback}")
        return fallback, True

    return preferred, False


TRAIN_DIR, TRAIN_DATA_AVAILABLE = select_dataset(PREFERRED_TRAIN_DIR, FALLBACK_TRAIN_DIR, "train")
VAL_DIR, VAL_DATA_AVAILABLE = select_dataset(PREFERRED_VAL_DIR, FALLBACK_VAL_DIR, "validation")

print(f"BASE_DIR: {BASE_DIR}")
print(f"Selected TRAIN_DIR: {TRAIN_DIR} (has data: {TRAIN_DATA_AVAILABLE})")
print(f"Selected VAL_DIR: {VAL_DIR} (has data: {VAL_DATA_AVAILABLE})")
print(f"UPLOAD_DIR: {UPLOAD_DIR}")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        if model is None:
            return JSONResponse(
                status_code=503, 
                content={"error": "Model not loaded. Please check server logs."}
            )
        result = predict_image(model, file.file, class_names)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/retrain")
async def retrain(files: List[UploadFile] = File(...)):
    try:
        # Check if training data is available
        if not TRAIN_DATA_AVAILABLE:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Training data not found in {TRAIN_DIR}. The training images are not included in the Docker image because they are excluded by .gitignore. To enable retraining, you need to: 1) Use Git LFS to track the data directory, or 2) Include a minimal training dataset in the repository.",
                    "train_dir": TRAIN_DIR,
                    "val_dir": VAL_DIR,
                    "suggestion": "Add training data to repository using Git LFS: 'git lfs track \"data/train/**\" && git lfs track \"data/validation/**\"'"
                }
            )
        if not VAL_DATA_AVAILABLE:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Validation data not found in {VAL_DIR}. Please ensure validation images are included in the deployment.",
                    "train_dir": TRAIN_DIR,
                    "val_dir": VAL_DIR
                }
            )
        
        # Save uploaded files
        uploaded_files = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded_files.append(file_path)

        num_classes = len(class_names)
        # Use absolute path for model save
        if os.path.exists("/app/models"):
            new_model_path = "/app/models/best_model.h5"
        else:
            new_model_path = os.path.join(BASE_DIR, "models", "best_model.h5")

        # Call retrain_model to train from scratch
        # Note: Using 1 epoch for Render free tier to avoid timeout
        # For production with more epochs, consider using background jobs
        print(f"Starting retraining with 1 epoch (reduced for timeout limits)...")
        result = retrain_model(
            TRAIN_DIR, 
            VAL_DIR, 
            num_classes, 
            new_model_path,
            epochs=1  # Reduced to 1 for Render free tier timeout limits
        )
        print(f"Retraining completed successfully")

        # Reload the model after retraining
        # Check if model was saved to Docker path or relative path
        if os.path.exists("/app/models/best_model.h5"):
            reload_path = "/app/models/best_model.h5"
        elif os.path.exists("models/best_model.h5"):
            reload_path = "models/best_model.h5"
        else:
            # Try relative path from project root
            reload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), new_model_path)
        
        try:
            load_model(reload_path)
        except Exception as e:
            print(f"Warning: Could not reload model after retraining: {e}")
            # Model might still be usable, continue

        return {
            "message": result["message"],
            "uploaded_files": len(uploaded_files),
            "final_train_accuracy": result["final_train_accuracy"],
            "final_val_accuracy": result["final_val_accuracy"],
            "final_train_loss": result.get("final_train_loss", 0),
            "final_val_loss": result.get("final_val_loss", 0),
            "epochs_trained": result["epochs_trained"],
            "history": result.get("history", {})
        }

    except Exception as e:
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__
        }
        print(f"Error in retrain endpoint: {e}")
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content=error_details)


@app.get("/")
def home():
    """Health check endpoint for Railway"""
    return {"message": "Vegetable Classification API is running", "status": "healthy"}

@app.head("/")
def health_head():
    """HEAD endpoint for Railway health checks"""
    return Response(status_code=200)

@app.get("/health")
def health():
    """Explicit health check endpoint"""
    return {"status": "healthy", "model_loaded": model is not None}