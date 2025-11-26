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
    import sys
    
    # Determine base directory - works in Docker and locally
    if os.path.exists("/app"):
        base_dir = "/app"
    else:
        base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Create model in both locations to be safe
    out_path1 = os.path.join(base_dir, "models", "best_model.h5")
    out_path2 = "/app/models/best_model.h5" if os.path.exists("/app") else None
    
    os.makedirs(os.path.dirname(out_path1), exist_ok=True)
    if out_path2:
        os.makedirs(os.path.dirname(out_path2), exist_ok=True)
    
    print(f"Creating minimal dummy model...")
    print(f"Base directory: {base_dir}")
    print(f"Primary output path: {out_path1}")
    if out_path2:
        print(f"Secondary output path: {out_path2}")
    
    try:
        model = create_minimal_model(num_classes=15)
        
        # Save to primary location
        model.save(out_path1)
        print(f"✓ Saved model to {out_path1}")
        
        # Also save to /app/models if in Docker
        if out_path2 and out_path2 != out_path1:
            model.save(out_path2)
            print(f"✓ Saved model to {out_path2}")
        
        # Verify at least one file exists
        if os.path.exists(out_path1):
            size_mb = os.path.getsize(out_path1) / (1024 * 1024)
            print(f"✓ Verified: Model file exists at {out_path1} ({size_mb:.2f} MB)")
            print("NOTE: This is a dummy model with random weights. Accuracy will be very low.")
            print("Use /retrain endpoint to train a proper model.")
            sys.exit(0)
        elif out_path2 and os.path.exists(out_path2):
            size_mb = os.path.getsize(out_path2) / (1024 * 1024)
            print(f"✓ Verified: Model file exists at {out_path2} ({size_mb:.2f} MB)")
            sys.exit(0)
        else:
            print(f"✗ ERROR: Model file was not created at either location")
            print(f"  Checked: {out_path1}")
            if out_path2:
                print(f"  Checked: {out_path2}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ ERROR creating model: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

