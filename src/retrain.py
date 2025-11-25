from src.preprocessing import get_data_generators
from src.model import build_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrain_model(train_dir, val_dir, num_classes, model_save_path, epochs=10):
    """
    Retrain the model from scratch using existing training data.
    
    Args:
        train_dir: Directory containing training data
        val_dir: Directory containing validation data
        num_classes: Number of classes
        model_save_path: Path to save the retrained model
        epochs: Number of training epochs
    """
    try:
        logger.info("Starting model retraining from scratch...")
        logger.info(f"Training directory: {train_dir}")
        logger.info(f"Validation directory: {val_dir}")
        
        # Get data generators
        train_gen, val_gen = get_data_generators(train_dir, val_dir)
        logger.info(f"Training samples: {train_gen.samples}")
        logger.info(f"Validation samples: {val_gen.samples}")
        
        # Build new model from scratch
        logger.info("Building new model from scratch...")
        model = build_model(num_classes)
        logger.info("Model built successfully")
        
        # Setup callbacks - ensure directory exists for checkpoint
        model_dir = os.path.dirname(model_save_path)
        if model_dir:
            os.makedirs(model_dir, exist_ok=True)
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
            ModelCheckpoint(model_save_path, monitor='val_loss', save_best_only=True, verbose=1)
        ]
        
        logger.info(f"Starting training for {epochs} epochs...")
        
        # Train the model
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        model.save(model_save_path)
        logger.info(f"Model retrained and saved to {model_save_path}")
        
        # Log final metrics
        final_train_acc = history.history['accuracy'][-1]
        final_val_acc = history.history['val_accuracy'][-1]
        logger.info(f"Final training accuracy: {final_train_acc:.4f}")
        logger.info(f"Final validation accuracy: {final_val_acc:.4f}")
        
        return {
            "message": "Model retrained and saved successfully",
            "final_train_accuracy": float(final_train_acc),
            "final_val_accuracy": float(final_val_acc),
            "final_train_loss": float(history.history['loss'][-1]),
            "final_val_loss": float(history.history['val_loss'][-1]),
            "epochs_trained": len(history.history['accuracy']),
            "history": {
                "accuracy": [float(x) for x in history.history['accuracy']],
                "val_accuracy": [float(x) for x in history.history['val_accuracy']],
                "loss": [float(x) for x in history.history['loss']],
                "val_loss": [float(x) for x in history.history['val_loss']]
            }
        }
    except Exception as e:
        logger.error(f"Error during retraining: {str(e)}", exc_info=True)
        raise
    