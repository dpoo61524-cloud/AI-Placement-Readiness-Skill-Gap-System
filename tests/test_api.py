import os
import sys
import json
import time
from fastapi.testclient import TestClient

# Add workspace root dynamically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import FastAPI app
from backend.main import app

client = TestClient(app)

def run_api_tests():
    print("==================================================")
    print("STARTING BACKEND API ENDPOINT VERIFICATION TESTS")
    print("==================================================")
    
    # Clear cache file to ensure a clean cold-start/cache-miss measurement
    cache_db_path = "data/cache.db"
    if os.path.exists(cache_db_path):
        try:
            os.remove(cache_db_path)
            print("Cleared SQLite cache file for clean test run.")
        except Exception as e:
            print(f"Could not clear cache database: {e}")

    # 1. Health check
    print("\n--- Test 1: GET /health ---")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    # Check if dummy PDF exists from Part 1
    dummy_pdf_path = "data/dummy_resume.pdf"
    if not os.path.exists(dummy_pdf_path):
        print(f"Warning: {dummy_pdf_path} not found. Creating it programmatically...")
        from tests.test_pipeline import generate_dummy_resume_pdf
        generate_dummy_resume_pdf(dummy_pdf_path)
        
    # 2. Parse Resume PDF
    print("\n--- Test 2: POST /parse-resume ---")
    with open(dummy_pdf_path, "rb") as f:
        response = client.post("/parse-resume", files={"file": (os.path.basename(dummy_pdf_path), f, "application/pdf")})
    print(f"Status: {response.status_code}")
    parsed_data = response.json()
    print(f"Parsed Specialization: {parsed_data['features']['specialization']}")
    print(f"Parsed Skills count: {len(parsed_data['resume_skills'])}")
    assert response.status_code == 200
    assert "features" in parsed_data
    assert "resume_skills" in parsed_data
    
    # 3. Predict Readiness
    print("\n--- Test 3: POST /predict ---")
    payload = parsed_data["features"]
    response = client.post("/predict", json=payload)
    print(f"Status: {response.status_code}")
    pred_data = response.json()
    print(f"Readiness Score: {pred_data['readiness_probability'] * 100:.2f}%")
    print(f"SHAP Contributions keys: {list(pred_data['contributions'].keys())}")
    assert response.status_code == 200
    assert "readiness_probability" in pred_data
    assert "contributions" in pred_data
    
    # 4. Skill Gap
    print("\n--- Test 4: POST /skill-gap ---")
    gap_payload = {
        "resume_skills": parsed_data["resume_skills"],
        "job_description": "Wanted Software Engineer with skillsets: Python, React, SQL, AWS, Kubernetes, Git."
    }
    response = client.post("/skill-gap", json=gap_payload)
    print(f"Status: {response.status_code}")
    gap_data = response.json()
    print(f"Matched count: {len(gap_data['matched'])}")
    print(f"Missing count: {len(gap_data['missing'])}")
    assert response.status_code == 200
    assert "matched" in gap_data
    assert "missing" in gap_data
    
    # 5. Recommendations
    print("\n--- Test 5: POST /recommendations ---")
    missing_mapped = [
        {"required_skill": s["required_skill"], "importance_weight": s["importance_weight"]}
        for s in gap_data["missing"]
    ]
    rec_payload = {
        "missing_skills": missing_mapped,
        "student_cgpa": parsed_data["features"]["CGPA"]
    }
    response = client.post("/recommendations", json=rec_payload)
    print(f"Status: {response.status_code}")
    rec_data = response.json()
    print(f"Project level recommendation: {rec_data['project_difficulty_level']}")
    print(f"Curriculum weeks count: {len(rec_data['weeks'])}")
    assert response.status_code == 200
    assert "weeks" in rec_data
    assert "text_summary" in rec_data
    
    # 6. Full Analysis (Cache Miss vs Cache Hit check)
    print("\n--- Test 6: POST /full-analysis (CACHE MISS) ---")
    mock_jd_text = "Wanted Developer: Python, Spring Boot, SQL, Kubernetes, AWS, Teamwork, Presentation."
    
    start_time = time.time()
    with open(dummy_pdf_path, "rb") as f:
        response = client.post(
            "/full-analysis", 
            files={"resume": (os.path.basename(dummy_pdf_path), f, "application/pdf")},
            data={"job_description": mock_jd_text}
        )
    miss_duration = time.time() - start_time
    print(f"Status: {response.status_code}")
    print(f"Cache Miss Execution Time: {miss_duration:.4f} seconds")
    assert response.status_code == 200
    full_data = response.json()
    assert "student_profile" in full_data
    assert "recommendation_plan" in full_data
    
    print("\n--- Test 7: POST /full-analysis (CACHE HIT Verification) ---")
    start_time = time.time()
    with open(dummy_pdf_path, "rb") as f:
        response = client.post(
            "/full-analysis", 
            files={"resume": (os.path.basename(dummy_pdf_path), f, "application/pdf")},
            data={"job_description": mock_jd_text}
        )
    hit_duration = time.time() - start_time
    print(f"Status: {response.status_code}")
    print(f"Cache Hit Execution Time: {hit_duration:.4f} seconds")
    assert response.status_code == 200
    # Cache hit should be fast (e.g. < 50ms) compared to embedding model computation (~0.5 - 2.0s)
    print(f"Speedup Factor: {miss_duration / hit_duration:.1f}x faster!")
    assert hit_duration < miss_duration
    
    # 7. History check
    print("\n--- Test 8: GET /history ---")
    response = client.get("/history")
    print(f"Status: {response.status_code}")
    history_data = response.json()
    print(f"History entries returned: {len(history_data)}")
    print(f"First entry file: {history_data[0]['resume_filename']}")
    assert response.status_code == 200
    assert len(history_data) > 0
    
    print("\n==================================================")
    print("ALL ENDPOINT VERIFICATION TESTS COMPLETED SUCCESSFULY!")
    print("==================================================")

if __name__ == "__main__":
    run_api_tests()
