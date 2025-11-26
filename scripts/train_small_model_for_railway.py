import os

from tensorflow.keras import layers, models

from src.preprocessing import get_data_generators


def build_small_model(num_classes: int = 15):
    inputs = layers.Input(shape=(224, 224, 3))
    x = layers.Conv2D(16, 3, activation="relu")(inputs)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(32, 3, activation="relu")(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Flatten()(x)
    x = layers.Dense(64, activation="relu")(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)
    model = models.Model(inputs, outputs)
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    train_dir = os.path.join(base_dir, "data", "train_min")
    val_dir = os.path.join(base_dir, "data", "validation_min")

    print("Using train dir:", train_dir)
    print("Using val dir:", val_dir)

    train_gen, val_gen = get_data_generators(train_dir, val_dir)

    model = build_small_model(num_classes=15)

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=3,
    )

    # Save to the path expected by the API (/app/models/best_model.h5)
    out_path = os.path.join(base_dir, "models", "best_model.h5")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    model.save(out_path)
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Saved small model to {out_path} ({size_mb:.2f} MB)")


