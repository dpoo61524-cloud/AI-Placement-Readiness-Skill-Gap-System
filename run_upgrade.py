import os
import subprocess
import sys

def main():
    print("=== STARTING AI PLACEMENT SYSTEM UPGRADE ===")
    
    # 1. Generate 20,000 synthetic data records
    print("\n[1/3] Generating 20,000 synthetic dataset samples...")
    subprocess.run([sys.executable, "src/data_prep.py"], check=True)
    
    # 2. Retrain machine learning models
    print("\n[2/3] Re-training ML classification models (Random Forest / XGBoost)...")
    subprocess.run([sys.executable, "src/train_model.py"], check=True)
    
    # 3. Clean up database caches to ensure fresh runs map to the new model
    db_path = "data/cache.db"
    if os.path.exists(db_path):
        print(f"\n[3/3] Clearing database cache at {db_path} to avoid stale predictions...")
        try:
            os.remove(db_path)
            print("Database cache cleared successfully.")
        except Exception as e:
            print(f"Could not delete database file: {e}")
    else:
        print("\n[3/3] Database cache is clean.")

    print("\n=== SYSTEM UPGRADE COMPLETED SUCCESSFULY ===")

if __name__ == "__main__":
    main()
