from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from src.prediction import load_trained_model, predict_image
from src.retrain import retrain_model
import os
from typing import List

app = FastAPI(title="Vegetable Classification API")

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
# Use absolute paths for Docker/Render
if os.path.exists("/app"):
    BASE_DIR = "/app"  # Docker environment
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__)) if os.path.dirname(__file__) else os.getcwd()

TRAIN_DIR = os.path.join(BASE_DIR, "data", "train")
VAL_DIR = os.path.join(BASE_DIR, "data", "validation")
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "retrain_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Debug: Print paths for troubleshooting
print(f"BASE_DIR: {BASE_DIR}")
print(f"TRAIN_DIR: {TRAIN_DIR} (exists: {os.path.exists(TRAIN_DIR)})")
print(f"VAL_DIR: {VAL_DIR} (exists: {os.path.exists(VAL_DIR)})")


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
        # Check if training data directories exist
        if not os.path.exists(TRAIN_DIR):
            return JSONResponse(
                status_code=400,
                content={"error": f"Training data directory not found: {TRAIN_DIR}. Please ensure data/train directory exists in the deployment."}
            )
        if not os.path.exists(VAL_DIR):
            return JSONResponse(
                status_code=400,
                content={"error": f"Validation data directory not found: {VAL_DIR}. Please ensure data/validation directory exists in the deployment."}
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
        result = retrain_model(
            TRAIN_DIR, 
            VAL_DIR, 
            num_classes, 
            new_model_path,
            epochs=10
        )

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
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/")
def home():
    return {"message": "Vegetable Classification API is running "}