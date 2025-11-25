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

    if pred_index >= len(class_names):
        raise ValueError("Predicted index out of class range")

    # Return top prediction and all probabilities
    return {
        "prediction": class_names[pred_index],
        "confidence": float(probabilities[pred_index]),
        "all_probabilities": {
            class_names[i]: float(prob) for i, prob in enumerate(probabilities)
        }
    }