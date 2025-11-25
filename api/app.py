from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from src.prediction import load_trained_model, predict_image
from src.retrain import retrain_model
import os
from typing import List

app = FastAPI(title="Vegetable Classification API")

MODEL_PATH = "/app/models/best_model.h5"
model = None

def load_model():
    """Load or reload the model"""
    global model
    model = load_trained_model(MODEL_PATH)

# Load model at startup
load_model()

# REAL CLASS LIST (MUST MATCH TRAINING ORDER)
class_names = [
    "Bean", "Bitter_Gourd", "Bottle_Gourd", "Brinjal", "Broccoli",
    "Cabbage", "Capsicum", "Carrot", "Cauliflower", "Cucumber",
    "Papaya", "Potato", "Pumpkin", "Radish", "Tomato"
]

# Paths to training and test data (match your folder structure)
TRAIN_DIR = "data/train"
VAL_DIR = "data/validation"
UPLOAD_DIR = "data/retrain_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        result = predict_image(model, file.file, class_names)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/retrain")
async def retrain(files: List[UploadFile] = File(...)):
    try:
        # Save uploaded files
        uploaded_files = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded_files.append(file_path)
        
        num_classes = len(class_names)
        new_model_path = "models/best_model.h5"

        # Call retrain_model to train from scratch
        result = retrain_model(
            TRAIN_DIR, 
            VAL_DIR, 
            num_classes, 
            new_model_path,
            epochs=10
        )

        # Reload the model after retraining
        load_model()

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