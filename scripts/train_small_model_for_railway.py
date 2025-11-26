import os

from tensorflow.keras import layers, models

from src.preprocessing import get_data_generators


def build_small_model(num_classes: int = 15):
    """Build a small but effective model for Railway deployment"""
    inputs = layers.Input(shape=(224, 224, 3))
    
    # Better architecture for accuracy while keeping size reasonable
    x = layers.Conv2D(32, 3, activation="relu", padding="same")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Dropout(0.25)(x)
    
    x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Dropout(0.25)(x)
    
    x = layers.Conv2D(128, 3, activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Dropout(0.5)(x)
    
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.BatchNormalization()(x)
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

    model = build_small_model(num_classes=15)

    # Use minimal training to reduce memory usage on Railway
    # Single epoch with smaller batch processing
    import tensorflow as tf
    # Limit memory growth to prevent OOM
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(f"GPU config error: {e}")
    
    # Train with multiple epochs for better accuracy
    # Use callbacks to save best model and early stopping
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True, verbose=1),
        ModelCheckpoint(out_path, monitor='val_loss', save_best_only=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-7, verbose=1)
    ]
    
    # Train for up to 5 epochs (will stop early if validation doesn't improve)
    # This balances accuracy with build time
    print("Starting training with early stopping...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=5,  # Will stop early if no improvement
        callbacks=callbacks,
        verbose=1
    )
    
    # Load the best model (saved by ModelCheckpoint)
    from tensorflow.keras.models import load_model
    if os.path.exists(out_path):
        model = load_model(out_path)
        print("✓ Loaded best model from checkpoint")
        
        # Evaluate final accuracy
        final_train_acc = history.history['accuracy'][-1] if 'accuracy' in history.history else 0
        final_val_acc = history.history['val_accuracy'][-1] if 'val_accuracy' in history.history else 0
        print(f"Final training accuracy: {final_train_acc:.4f}")
        print(f"Final validation accuracy: {final_val_acc:.4f}")
    else:
        print("Warning: Best model checkpoint not found, using current model")

    # Save to the path expected by the API (/app/models/best_model.h5)
    out_path = os.path.join(base_dir, "models", "best_model.h5")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    model.save(out_path)
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Saved small model to {out_path} ({size_mb:.2f} MB)")


