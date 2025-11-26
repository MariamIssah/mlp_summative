import os

from tensorflow.keras import layers, models

from src.preprocessing import get_data_generators


def build_small_model(num_classes: int = 15):
    """Build a balanced model for Railway - good accuracy, reasonable size"""
    inputs = layers.Input(shape=(224, 224, 3))
    
    # Optimized architecture - good accuracy without being too heavy
    x = layers.Conv2D(32, 3, activation="relu")(inputs)
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Dropout(0.2)(x)
    
    x = layers.Conv2D(64, 3, activation="relu")(x)
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Conv2D(128, 3, activation="relu")(x)
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Dropout(0.4)(x)
    
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)
    
    model = models.Model(inputs, outputs)
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


if __name__ == "__main__":
    import tensorflow as tf
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    train_dir = os.path.join(base_dir, "data", "train_min")
    val_dir = os.path.join(base_dir, "data", "validation_min")

    print("Using train dir:", train_dir)
    print("Using val dir:", val_dir)

    # Use smaller batch size to reduce memory usage
    IMAGE_SIZE = (224, 224)
    BATCH_SIZE = 8  # Reduced from 32 to save memory
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        zoom_range=0.2,
        horizontal_flip=True
    )
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_gen = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    val_gen = val_datagen.flow_from_directory(
        val_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    # Define output path first
    out_path = os.path.join(base_dir, "models", "best_model.h5")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    model = build_small_model(num_classes=15)

    # Configure TensorFlow for Railway
    import tensorflow as tf
    # Limit memory growth to prevent OOM
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(f"GPU config error: {e}")
    
    # Train with callbacks for better accuracy
    # Use fewer epochs to avoid Railway timeout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True, verbose=1),
        ModelCheckpoint(out_path, monitor='val_loss', save_best_only=True, verbose=1)
    ]
    
    # Train for 3 epochs max (will stop early if validation doesn't improve)
    # This balances accuracy with Railway build time limits
    print("Starting training (max 3 epochs with early stopping)...")
    try:
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=3,  # Reduced to 3 to avoid Railway timeout
            callbacks=callbacks,
            verbose=1
        )
        
        # Load the best model (saved by ModelCheckpoint)
        from tensorflow.keras.models import load_model
        if os.path.exists(out_path):
            model = load_model(out_path)
            print("✓ Loaded best model from checkpoint")
            
            # Evaluate final accuracy
            if 'accuracy' in history.history and len(history.history['accuracy']) > 0:
                final_train_acc = history.history['accuracy'][-1]
                final_val_acc = history.history['val_accuracy'][-1] if 'val_accuracy' in history.history else 0
                print(f"Final training accuracy: {final_train_acc:.4f}")
                print(f"Final validation accuracy: {final_val_acc:.4f}")
        else:
            print("Warning: Best model checkpoint not found, saving current model...")
            model.save(out_path)
    except Exception as e:
        print(f"Training error: {e}")
        print("Saving current model anyway...")
        model.save(out_path)
        raise
    
    # Final save to ensure model is saved
    if not os.path.exists(out_path):
        model.save(out_path)
    
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"✓ Saved model to {out_path} ({size_mb:.2f} MB)")


