import os

from tensorflow.keras import layers, models

from src.preprocessing import get_data_generators


def build_small_model(num_classes: int = 15):
    """Build a very small model to minimize memory usage on Railway"""
    inputs = layers.Input(shape=(224, 224, 3))
    # Even smaller architecture
    x = layers.Conv2D(8, 3, activation="relu")(inputs)  # Reduced from 16
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Conv2D(16, 3, activation="relu")(x)  # Reduced from 32
    x = layers.MaxPooling2D(2, 2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(32, activation="relu")(x)  # Reduced from 64
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
    
    # Train with just 1 epoch to minimize memory usage
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=1,  # Reduced to 1 epoch to save memory
        verbose=1
    )

    # Save to the path expected by the API (/app/models/best_model.h5)
    out_path = os.path.join(base_dir, "models", "best_model.h5")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    model.save(out_path)
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Saved small model to {out_path} ({size_mb:.2f} MB)")


