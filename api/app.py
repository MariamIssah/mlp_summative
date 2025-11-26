from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, Response
from src.prediction import load_trained_model, predict_image
from src.retrain import retrain_model
import os
from typing import List
import traceback
import threading

app = FastAPI(title="Vegetable Classification API")

# Log port for Railway debugging
PORT = int(os.getenv("PORT", 8000))
print(f"Starting server on port {PORT}")

@app.on_event("startup")
async def startup_event():
    """Log startup completion for Railway health checks"""
    print("FastAPI application startup complete")
    print("Health check endpoints are ready")
    print("Model loading may still be in progress")
    print("Service is ready to accept requests")

# Determine BASE_DIR first (needed for model paths)
if os.path.exists("/app"):
    BASE_DIR = "/app"  # Docker/Railway container
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__)) if os.path.dirname(__file__) else os.getcwd()

# Determine model path - works for both Docker and Render
MODEL_PATH = None
possible_model_paths = [
    "/app/models/best_model.h5",  # Docker/Railway path (created during build)
    os.path.join(BASE_DIR, "models", "best_model.h5"),  # Relative to BASE_DIR
    "models/best_model.h5",  # Relative path
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best_model.h5"),  # Fallback
]

# Find the first existing model path
for path in possible_model_paths:
    if path and os.path.exists(path):
        MODEL_PATH = path
        print(f"Found model file at: {path}")
        break

if not MODEL_PATH:
    MODEL_PATH = "/app/models/best_model.h5"  # Default to Docker path
    print(f"No existing model found, will use default path: {MODEL_PATH}")

model = None

def load_model(model_path=None):
    """Load or reload the model using the existing trained file.

    This is intentionally simple so it works both locally and on Railway
    with the already-trained model file (best_model.h5).
    """
    global model, MODEL_PATH
    if model_path:
        MODEL_PATH = model_path

    # Try multiple possible model paths
    possible_paths = [
        MODEL_PATH,
        "/app/models/best_model.h5",
        os.path.join(BASE_DIR, "models", "best_model.h5"),
        "models/best_model.h5",
    ]
    
    # Remove duplicates and None values
    possible_paths = list(dict.fromkeys([p for p in possible_paths if p]))
    
    print(f"Attempting to load model. Checking paths: {possible_paths}")
    
    for path in possible_paths:
        print(f"Checking if model exists at: {path}")
        if path and os.path.exists(path):
            file_size = os.path.getsize(path) / (1024 * 1024)  # Size in MB
            print(f"Found model file at {path} ({file_size:.2f} MB). Attempting to load...")
            try:
                model_local = load_trained_model(path)
                model = model_local
                MODEL_PATH = path
                print(f"✓ Model loaded successfully from {path}")
                return True
            except Exception as e:
                print(f"✗ Error loading model from {path}: {e}")
                import traceback
                traceback.print_exc()
                continue
        else:
            print(f"  Model file not found at: {path}")
    
    print(f"✗ Model not found in any of the expected locations: {possible_paths}")
    print("  Model will need to be created via /retrain endpoint")
    model = None
    return False

# Load model at startup
# For local development, load immediately; for Railway, load in background
if os.path.exists("models/best_model.h5") or not os.path.exists("/app"):
    # Local development - load immediately
    print("Loading model immediately (local development)...")
    try:
        load_model()
        print("Model loaded successfully at startup")
    except Exception as e:
        print(f"Failed to load model at startup: {e}")
        model = None
else:
    # Railway/Docker - try to load immediately, then retry in background if needed
    print("Attempting to load model on Railway/Docker...")
    model_loaded = load_model()
    
    if not model_loaded:
        # If immediate load failed, try in background (might be still training during build)
        def load_model_background():
            """Load model in background thread with retries"""
            import time
            max_retries = 5
            for attempt in range(max_retries):
                time.sleep(5 * (attempt + 1))  # Wait longer each retry
                print(f"Background model load attempt {attempt + 1}/{max_retries}...")
                if load_model():
                    print("Model loaded successfully in background")
                    return
            print("Failed to load model after all retries. Use /retrain endpoint to create a model.")
        
        model_loading_thread = threading.Thread(target=load_model_background, daemon=True)
        model_loading_thread.start()
        print("Model loading started in background thread (will retry if needed)")
    else:
        print("Model loaded successfully at startup")

# REAL CLASS LIST (MUST MATCH TRAINING ORDER - alphabetical by folder name)
# ImageDataGenerator uses alphabetical order of folder names
# This list must match the order returned by train_gen.class_indices
class_names = [
    "Bean", "Bitter_Gourd", "Bottle_Gourd", "Brinjal", "Broccoli",
    "Cabbage", "Capsicum", "Carrot", "Cauliflower", "Cucumber",
    "Papaya", "Potato", "Pumpkin", "Radish", "Tomato"
]
# Note: If predictions are wrong, the class order might not match the data generator's order
# The data generator uses alphabetical order of folder names in the training directory

# BASE_DIR already set above, no need to set again

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


@app.get("/model-info")
def model_info():
    """Get information about the loaded model"""
    if model is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Model not loaded", "model_path": MODEL_PATH}
        )
    
    # Try to get class indices from training data if available
    class_indices_info = {}
    try:
        from src.preprocessing import get_data_generators
        if TRAIN_DATA_AVAILABLE:
            train_gen, _ = get_data_generators(TRAIN_DIR, VAL_DIR)
            class_indices_info = train_gen.class_indices
    except:
        pass
    
    return {
        "model_loaded": True,
        "model_path": MODEL_PATH,
        "class_names": class_names,
        "num_classes": len(class_names),
        "data_generator_class_indices": class_indices_info,
        "note": "If predictions are wrong, verify class_names order matches data_generator_class_indices (alphabetical order)"
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        if model is None:
            return JSONResponse(
                status_code=503, 
                content={
                    "error": "Model not loaded. The model file is missing or failed to load.",
                    "model_path": MODEL_PATH,
                    "suggestion": "Use the /retrain endpoint to train a model first, or ensure a model file exists at the expected path."
                }
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
            os.makedirs("/app/models", exist_ok=True)
        else:
            new_model_path = os.path.join(BASE_DIR, "models", "best_model.h5")
            os.makedirs(os.path.dirname(new_model_path), exist_ok=True)

        # Call retrain_model to train from scratch
        # Note: Using 1 epoch for Railway free tier to avoid timeout
        # For production with more epochs, consider using background jobs
        print(f"Starting retraining with 1 epoch (reduced for Railway timeout limits)...")
        print(f"Training data: {TRAIN_DIR}, Validation data: {VAL_DIR}")
        print(f"Model will be saved to: {new_model_path}")
        
        try:
            result = retrain_model(
                TRAIN_DIR, 
                VAL_DIR, 
                num_classes, 
                new_model_path,
                epochs=1  # Reduced to 1 for Railway free tier timeout limits
            )
            print(f"Retraining completed successfully")
        except Exception as train_error:
            error_msg = f"Training failed: {str(train_error)}"
            print(error_msg)
            print(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={
                    "error": error_msg,
                    "error_type": type(train_error).__name__,
                    "suggestion": "Training may have timed out or run out of memory. Try with fewer images or run locally."
                }
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
            print("Model reloaded successfully after retraining")
            
            # Try to load and verify class indices from saved file
            try:
                import json
                class_indices_path = os.path.join(os.path.dirname(reload_path), "class_indices.json")
                if os.path.exists(class_indices_path):
                    with open(class_indices_path, 'r') as f:
                        saved_indices = json.load(f)
                    print(f"Class indices from training: {saved_indices}")
                    sorted_classes = sorted(saved_indices.items(), key=lambda x: x[1])
                    expected_order = [name for name, idx in sorted_classes]
                    print(f"Expected class order: {expected_order}")
                    print(f"Current class_names order: {class_names}")
                    if expected_order != class_names:
                        print(f"WARNING: Class order mismatch! Expected: {expected_order}, Got: {class_names}")
            except Exception as e:
                print(f"Could not load class indices: {e}")
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
    """Health check endpoint for Railway - responds immediately"""
    # Always return 200 OK - Railway needs this to keep container alive
    return JSONResponse(
        status_code=200,
        content={
            "message": "Vegetable Classification API is running", 
            "status": "healthy",
            "model_loaded": model is not None
        }
    )

@app.head("/")
def health_head():
    """HEAD endpoint for Railway health checks - critical for keeping container alive"""
    # Return 200 immediately - Railway uses this to verify service is alive
    return Response(status_code=200, headers={"Content-Type": "application/json"})

@app.get("/health")
def health():
    """Explicit health check endpoint - always returns healthy for Railway"""
    return {
        "status": "healthy", 
        "model_loaded": model is not None,
        "model_path": MODEL_PATH if model is not None else "No model loaded",
        "service": "vegetable-classification-api"
    }