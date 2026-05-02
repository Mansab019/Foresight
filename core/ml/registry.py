from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


# ── MODEL REGISTRY ───────────────────────────────────
# Add or swap models here without touching any other file
# Each model is wrapped in a Pipeline with StandardScaler
# StandardScaler normalises features — important for KNN and SVM

MODEL_REGISTRY = {

    'linear_regression': Pipeline([
        ('scaler', StandardScaler()),
        ('model', LinearRegression())
    ]),

    'random_forest': Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestRegressor(
            n_estimators=100,    # 100 decision trees
            max_depth=10,        # prevents overfitting
            random_state=42      # reproducible results
        ))
    ]),

    'knn': Pipeline([
        ('scaler', StandardScaler()),
        ('model', KNeighborsRegressor(
            n_neighbors=5,       # look at 5 nearest months
            weights='distance'   # closer months matter more
        ))
    ]),

    'svm': Pipeline([
        ('scaler', StandardScaler()),
        ('model', SVR(
            kernel='rbf',        # radial basis function kernel
            C=100,               # regularization parameter
            epsilon=0.1          # tolerance margin
        ))
    ]),

}