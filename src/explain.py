import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

# Force matplotlib to use a non-interactive backend
plt.switch_backend('Agg')

def load_explainer_assets(models_dir="models"):
    preprocessor_path = os.path.join(models_dir, 'preprocessor.joblib')
    model_path = os.path.join(models_dir, 'placement_model.pkl')
    
    if not os.path.exists(preprocessor_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Preprocessor or Model not found. Run train_model.py first.")
        
    preprocessor_meta = joblib.load(preprocessor_path)
    model = joblib.load(model_path)
    
    return preprocessor_meta, model

def explain_student_readiness(student_data, models_dir="models"):
    """
    Given a single student's features (as a pandas DataFrame),
    returns the predicted probability % and a dictionary of feature contributions.
    """
    preprocessor_meta, model = load_explainer_assets(models_dir)
    preprocessor = preprocessor_meta['preprocessor']
    feature_names = preprocessor_meta['feature_names']
    numerical_cols = preprocessor_meta['numerical_cols']
    categorical_cols = preprocessor_meta['categorical_cols']
    
    # Preprocess student data
    X_preprocessed = preprocessor.transform(student_data)
    
    # Prediction probability
    prob = model.predict_proba(X_preprocessed)[0, 1]
    
    # Initialize explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_preprocessed)
    
    # Handle SHAP multi-class/binary list structures robustly
    # For RF classifier, shap_values is typically a list of [neg_class_shap, pos_class_shap]
    if isinstance(shap_values, list):
        shap_vals_student = shap_values[1][0]
        base_value = explainer.expected_value[1]
    elif isinstance(shap_values, np.ndarray):
        if len(shap_values.shape) == 3:  # (samples, features, classes)
            shap_vals_student = shap_values[0, :, 1]
            base_value = explainer.expected_value[1]
        else:  # (samples, features)
            shap_vals_student = shap_values[0]
            base_value = explainer.expected_value
    else:
        raise TypeError("Unexpected SHAP values type returned.")
        
    # Map preprocessed features to SHAP values
    feature_shap = dict(zip(feature_names, shap_vals_student))
    
    # Aggregate one-hot encoded categoricals back to original feature name
    aggregated_contributions = {}
    
    # 1. Add numerical contributions
    for col in numerical_cols:
        val = student_data[col].values[0]
        # Format key as feature name and value (e.g. "CGPA (8.5)")
        aggregated_contributions[col] = {
            'value': float(val) if isinstance(val, (int, float, np.integer, np.floating)) else val,
            'contribution': float(feature_shap[col])
        }
        
    # 2. Add categorical contributions
    for col in categorical_cols:
        val = student_data[col].values[0]
        # Sum SHAP values of all OHE categories for this variable
        cat_shap_sum = 0.0
        for feat_name, shap_val in feature_shap.items():
            if feat_name.startswith(f"{col}_"):
                cat_shap_sum += shap_val
                
        aggregated_contributions[col] = {
            'value': str(val),
            'contribution': float(cat_shap_sum)
        }
        
    # Format return dictionary
    explanation = {
        'readiness_probability': float(prob),
        'base_probability': float(base_value),
        'contributions': aggregated_contributions
    }
    
    return explanation

def generate_shap_summary_plot(data_path="data/placement_data.csv", models_dir="models"):
    """
    Generates a SHAP summary plot for the test set to verify explainability works.
    """
    preprocessor_meta, model = load_explainer_assets(models_dir)
    preprocessor = preprocessor_meta['preprocessor']
    feature_names = preprocessor_meta['feature_names']
    
    df = pd.read_csv(data_path)
    X = df.drop(columns=['placed'])
    y = df['placed']
    
    # Take a sample of 200 items for the plot
    X_sample = X.sample(n=200, random_state=42)
    X_sample_preprocessed = preprocessor.transform(X_sample)
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample_preprocessed)
    
    # Resolve correct SHAP array
    if isinstance(shap_values, list):
        shap_vals_plot = shap_values[1]
    elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        shap_vals_plot = shap_values[:, :, 1]
    else:
        shap_vals_plot = shap_values
        
    plt.figure(figsize=(10, 6))
    shap.summary_plot(
        shap_vals_plot, 
        X_sample_preprocessed, 
        feature_names=feature_names, 
        show=False
    )
    
    output_plot_path = os.path.join(models_dir, 'shap_summary.png')
    plt.title("SHAP Feature Importance (Placement Probability)", fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(output_plot_path, dpi=150)
    plt.close()
    
    print(f"SHAP summary plot successfully saved to {output_plot_path}")

if __name__ == "__main__":
    # Test individual explanation
    print("Testing SHAP explanation on a sample student...")
    sample_student = pd.DataFrame([{
        'CGPA': 8.5,
        'backlogs': 0,
        'internships': 1,
        'projects': 2,
        'certifications': 1,
        'coding_score': 75.0,
        'communication_score': 80.0,
        'specialization': 'Computer Science'
    }])
    
    result = explain_student_readiness(sample_student)
    print(f"\nReadiness Probability: {result['readiness_probability'] * 100:.2f}%")
    print(f"Base Probability: {result['base_probability'] * 100:.2f}%")
    print("\nFeature Contributions:")
    for feat, info in result['contributions'].items():
        sign = "+" if info['contribution'] >= 0 else ""
        print(f"  {feat} (val: {info['value']}): {sign}{info['contribution'] * 100:.2f}%")
        
    print("\nGenerating SHAP Summary plot...")
    generate_shap_summary_plot()
