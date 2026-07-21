from core.ml.trainer import train_all_models
from core.ml.predictor import generate_predictions


def run_ml_pipeline(user, batch=None):
    """
    Master function — runs the complete ML pipeline
    Call this single function to:
      1. Load data from PostgreSQL
      2. Engineer features
      3. Train all 4 models
      4. Evaluate and compare
      5. Save best model
      6. Generate next month predictions
      7. Save predictions to database

    If batch is given, the whole pipeline runs only on that
    upload's transactions — its own model, its own predictions —
    completely separate from the user's main merged forecast.

    Usage:
      from core.ml.pipeline import run_ml_pipeline
      run_ml_pipeline(user)
      run_ml_pipeline(user, batch=some_import_batch)
    """

    print("\n" + "="*50)
    print("FORESIGHT ML PIPELINE STARTED")
    print("="*50)

    # Train all models and get the best one
    best_model, best_model_name, results = train_all_models(user, batch=batch)

    if best_model is None:
        print("Training failed — pipeline stopped.")
        return None

    # Generate and save predictions
    predictions = generate_predictions(user, best_model_name, batch=batch)

    print("\n" + "="*50)
    print("FORESIGHT ML PIPELINE COMPLETE")
    print(f"Best model: {best_model_name}")
    print(f"Predictions saved: {len(predictions)}")
    print("="*50 + "\n")

    return {
        'best_model': best_model_name,
        'results': results,
        'predictions': predictions,
    }