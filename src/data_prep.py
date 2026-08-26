import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_synthetic_data(num_samples=20000, seed=42):
    np.random.seed(seed)
    
    # Feature distributions
    cgpa = np.random.uniform(5.5, 10.0, num_samples)
    backlogs = np.random.choice([0, 1, 2, 3, 4, 5], size=num_samples, p=[0.72, 0.15, 0.07, 0.03, 0.02, 0.01])
    internships = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.52, 0.33, 0.12, 0.03])
    projects = np.random.choice([0, 1, 2, 3, 4, 5], size=num_samples, p=[0.08, 0.22, 0.35, 0.23, 0.09, 0.03])
    certifications = np.random.choice([0, 1, 2, 3, 4, 5], size=num_samples, p=[0.32, 0.35, 0.20, 0.09, 0.03, 0.01])
    
    # Scores correlate with CGPA and projects
    coding_score = np.clip(np.random.normal(48 + 5 * (cgpa - 7) + 3 * projects, 12, num_samples), 10, 100)
    communication_score = np.clip(np.random.normal(52 + 3.5 * (cgpa - 7) + 4 * internships, 10, num_samples), 10, 100)
    
    specializations = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil']
    specialization = np.random.choice(specializations, size=num_samples, p=[0.38, 0.24, 0.18, 0.10, 0.10])
    
    df = pd.DataFrame({
        'CGPA': cgpa,
        'backlogs': backlogs,
        'internships': internships,
        'projects': projects,
        'certifications': certifications,
        'coding_score': coding_score,
        'communication_score': communication_score,
        'specialization': specialization
    })
    
    # Compute logit logic for target label placement (placed)
    cgpa_norm = (df['CGPA'] - 7.5) / 1.2
    coding_norm = (df['coding_score'] - 60) / 15
    comm_norm = (df['communication_score'] - 60) / 12
    
    spec_val = df['specialization'].map({
        'Computer Science': 0.7,
        'Information Technology': 0.5,
        'Electronics': 0.1,
        'Mechanical': -0.4,
        'Civil': -0.5
    }).values
    
    logit = (
        1.8 * cgpa_norm
        - 2.2 * df['backlogs'].values
        + 1.2 * df['internships'].values
        + 0.7 * df['projects'].values
        + 0.5 * df['certifications'].values
        + 1.0 * coding_norm
        + 0.8 * comm_norm
        + spec_val
        - 0.6  # Balance bias
    )
    
    noise = np.random.normal(0, 0.85, num_samples)
    prob = 1 / (1 + np.exp(-(logit + noise)))
    
    df['placed'] = (prob >= 0.55).astype(int)
    return df

def perform_eda(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # Class Balance Plot
    plt.figure(figsize=(6, 4))
    sns.countplot(x='placed', data=df, palette='pastel')
    plt.title('Campus Placement Class Balance')
    plt.xlabel('Placement Status')
    plt.ylabel('Student Count')
    plt.savefig(os.path.join(output_dir, 'class_balance.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    # Correlation Matrix
    num_cols = ['CGPA', 'backlogs', 'internships', 'projects', 'certifications', 
                'coding_score', 'communication_score', 'placed']
    corr = df[num_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Matrix of Student Metrics')
    plt.savefig(os.path.join(output_dir, 'correlation_matrix.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"EDA plots saved in: {output_dir}")
    print(f"Class Balance:\n{df['placed'].value_counts(normalize=True)}")

if __name__ == "__main__":
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    print("Generating synthetic student placement dataset (20,000 samples)...")
    df = generate_synthetic_data(num_samples=20000, seed=42)
    
    csv_path = os.path.join(data_dir, "placement_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset successfully saved to: {csv_path}")
    
    print("\nPerforming exploratory data analysis (EDA)...")
    perform_eda(df, data_dir)
