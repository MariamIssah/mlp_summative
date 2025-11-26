import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

IMAGE_SIZE = (224, 224)

def load_trained_model(model_path):
    return load_model(model_path)

def predict_image(model, image_file, class_names):
    img = Image.open(image_file).convert("RGB").resize(IMAGE_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array, verbose=0)
    pred_index = int(np.argmax(preds[0]))
    
    # Get probabilities for all classes
    probabilities = preds[0].tolist()
    
    # Check if this looks like a dummy model (all probabilities very similar = random)
    max_prob = max(probabilities)
    min_prob = min(probabilities)
    prob_range = max_prob - min_prob
    is_likely_dummy = prob_range < 0.1  # If all probabilities are within 10%, likely dummy model

    if pred_index >= len(class_names):
        raise ValueError("Predicted index out of class range")

    result = {
        "prediction": class_names[pred_index],
        "confidence": float(probabilities[pred_index]),
        "all_probabilities": {
            class_names[i]: float(prob) for i, prob in enumerate(probabilities)
        }
    }
    
    # Add warning if model appears to be dummy/untrained
    if is_likely_dummy:
        result["warning"] = "Model appears to have random weights (dummy model). Predictions will be inaccurate. Please retrain the model using /retrain endpoint."
    
    return result