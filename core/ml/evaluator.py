import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def evaluate_model(model, X_test, y_test):
    """
    Evaluate a trained model on test data
    Returns MAE and RMSE — lower is better
    """

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    return {
        'mae': round(mae, 2),
        'rmse': round(rmse, 2),
        'predictions': predictions,
    }


def compare_models(results):
    """
    Compare all model results and return the best one
    Best = lowest MAE
    """

    best_model_name = min(results, key=lambda x: results[x]['mae'])

    print("\n" + "="*50)
    print("MODEL COMPARISON RESULTS")
    print("="*50)

    for name, metrics in results.items():
        marker = " ← WINNER" if name == best_model_name else ""
        print(f"{name:<25} MAE: {metrics['mae']:<10} RMSE: {metrics['rmse']}{marker}")

    print("="*50 + "\n")

    return best_model_name