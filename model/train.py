import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import mlflow
import os

def train_model(data_path: str, model_save_path: str):
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("fraud_detection_experiment")

    with mlflow.start_run():
        df = pd.read_csv(data_path)
        
        features = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
        X = df[features]
        y = df['isFraud']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42))
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("max_iter", 1000)
        mlflow.log_param("features", features)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
        joblib.dump(pipeline, model_save_path)
        
        mlflow.sklearn.log_model(pipeline, "logistic_regression_model")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "paysim.csv")
    model_save_path = os.path.join(base_dir, "model_artifacts", "model.joblib")
    
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}.")
        print("Creating a dummy dataset for testing...")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        import numpy as np
        np.random.seed(42)
        n_samples = 1000
        dummy_data = pd.DataFrame({
            'amount': np.random.uniform(10, 10000, n_samples),
            'oldbalanceOrg': np.random.uniform(100, 50000, n_samples),
            'newbalanceOrig': np.random.uniform(100, 50000, n_samples),
            'oldbalanceDest': np.random.uniform(100, 50000, n_samples),
            'newbalanceDest': np.random.uniform(100, 50000, n_samples),
            'isFraud': np.random.choice([0, 1], n_samples, p=[0.95, 0.05])
        })
        dummy_data.to_csv(data_path, index=False)
        print("Dummy dataset created! NOTE: For real results, replace it with the actual Kaggle PaySim dataset.")

    print(f"Starting training with data from {data_path}...")
    train_model(data_path, model_save_path)
    print(f"Training completed successfully! Model saved to {model_save_path}")
