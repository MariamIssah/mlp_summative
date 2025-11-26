"""
Create a minimal dummy model that can at least load and make predictions
This is a fallback if training fails during Docker build
"""
import os
import tensorflow as tf
from tensorflow.keras import layers, models

def create_minimal_model(num_classes=15):
    """Create the smallest possible model that can load and predict"""
    model = models.Sequential([
        layers.Input(shape=(224, 224, 3)),
        layers.Flatten(),
        layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    out_path = os.path.join(base_dir, "models", "best_model.h5")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    print("Creating minimal dummy model...")
    model = create_minimal_model(num_classes=15)
    model.save(out_path)
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Created minimal model at {out_path} ({size_mb:.2f} MB)")
    print("NOTE: This is a dummy model with random weights. Accuracy will be very low.")
    print("Use /retrain endpoint to train a proper model.")

