import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def train_and_evaluate(data_path, models_dir):
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Load data
    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    
    X = df.drop(columns=['placed'])
    y = df['placed']
    
    # 2. Identify numerical and categorical columns
    numerical_cols = ['CGPA', 'backlogs', 'internships', 'projects', 'certifications', 
                      'coding_score', 'communication_score']
    categorical_cols = ['specialization']
    
    # 3. Define Preprocessing Pipeline
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )
    
    # 4. Train-Test Split (stratified 80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    
    # 5. Fit preprocessor and save
    print("Fitting preprocessing pipeline...")
    X_train_preprocessed = preprocessor.fit_transform(X_train)
    X_test_preprocessed = preprocessor.transform(X_test)
    
    # Get feature names after one-hot encoding for later SHAP/feature mapping
    ohe = preprocessor.named_transformers_['cat'].named_steps['onehot']
    encoded_cat_features = list(ohe.get_feature_names_out(categorical_cols))
    feature_names = numerical_cols + encoded_cat_features
    
    # Save the fitted preprocessor & feature names list
    preprocessor_meta = {
        'preprocessor': preprocessor,
        'feature_names': feature_names,
        'numerical_cols': numerical_cols,
        'categorical_cols': categorical_cols
    }
    preprocessor_path = os.path.join(models_dir, 'preprocessor.joblib')
    joblib.dump(preprocessor_meta, preprocessor_path)
    print(f"Saved preprocessing pipeline to {preprocessor_path}")
    
    # 6. Model Training & Comparison
    print("\nTraining candidate models...")
    
    rf = RandomForestClassifier(random_state=42)
    xgb = XGBClassifier(random_state=42, eval_metric='logloss')
    
    rf.fit(X_train_preprocessed, y_train)
    xgb.fit(X_train_preprocessed, y_train)
    
    # Evaluation function
    def get_metrics(model, X_val, y_val):
        preds = model.predict(X_val)
        probs = model.predict_proba(X_val)[:, 1]
        return {
            'accuracy': accuracy_score(y_val, preds),
            'precision': precision_score(y_val, preds),
            'recall': recall_score(y_val, preds),
            'f1': f1_score(y_val, preds),
            'roc_auc': roc_auc_score(y_val, probs)
        }
    
    rf_metrics = get_metrics(rf, X_test_preprocessed, y_test)
    xgb_metrics = get_metrics(xgb, X_test_preprocessed, y_test)
    
    print("\n--- Model Performance Comparison ---")
    print(f"Random Forest:")
    for k, v in rf_metrics.items():
        print(f"  {k.capitalize()}: {v:.4f}")
    print(f"XGBoost:")
    for k, v in xgb_metrics.items():
        print(f"  {k.capitalize()}: {v:.4f}")
        
    # 7. Select Best Model based on F1-score
    if xgb_metrics['f1'] >= rf_metrics['f1']:
        print("\nSelecting XGBoost for Hyperparameter Tuning (higher F1 score)...")
        best_base_model = XGBClassifier(random_state=42, eval_metric='logloss')
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.05, 0.1, 0.2]
        }
        model_type = 'xgb'
    else:
        print("\nSelecting Random Forest for Hyperparameter Tuning (higher F1 score)...")
        best_base_model = RandomForestClassifier(random_state=42)
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [5, 10, None],
            'min_samples_split': [2, 5, 10]
        }
        model_type = 'rf'
        
    # 8. GridSearchCV Tuning
    print(f"Running GridSearchCV for {best_base_model.__class__.__name__}...")
    grid_search = GridSearchCV(
        estimator=best_base_model,
        param_grid=param_grid,
        cv=5,
        scoring='f1',
        n_jobs=-1
    )
    grid_search.fit(X_train_preprocessed, y_train)
    
    best_tuned_model = grid_search.best_estimator_
    print(f"Best Hyperparameters: {grid_search.best_params_}")
    
    # 9. Final Test Set Evaluation
    final_metrics = get_metrics(best_tuned_model, X_test_preprocessed, y_test)
    print("\n--- Final Tuned Model Performance on Test Set ---")
    for k, v in final_metrics.items():
        print(f"  {k.capitalize()}: {v:.4f}")
        
    # 10. Save the final model
    model_path = os.path.join(models_dir, 'placement_model.pkl')
    joblib.dump(best_tuned_model, model_path)
    print(f"Saved tuned model to {model_path}")

if __name__ == "__main__":
    real_data_path = os.path.join("data", "real_placement_data.csv")
    synth_data_path = os.path.join("data", "placement_data.csv")
    data_path = real_data_path if os.path.exists(real_data_path) else synth_data_path
    models_dir = "models"
    print(f"Training placement prediction model using dataset: {data_path}")
    train_and_evaluate(data_path, models_dir)
