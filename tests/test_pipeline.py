import os
import json
import pandas as pd
from fpdf import FPDF

# Add workspace root to python path dynamically
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from src.resume_parser import parse_resume_pdf, parse_job_description
from src.explain import explain_student_readiness
from src.skill_gap import analyze_skill_gap

def generate_dummy_resume_pdf(output_path="data/dummy_resume.pdf"):
    """
    Creates a dummy student resume PDF file for test parsing.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Siddharth Sharma", ln=1, align="C")
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt="Email: siddharth.sharma@email.com | Phone: +91 9876543210", ln=1, align="C")
    pdf.cell(200, 5, txt="Education: Bachelor of Technology in Computer Science & Engineering", ln=1, align="C")
    pdf.cell(200, 5, txt="CGPA: 8.85 / 10 | Backlogs: 0", ln=1, align="C")
    pdf.ln(5)
    
    # Skills section
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Skills", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt="Languages: Python, Java, SQL, Javascript, C++", ln=1)
    pdf.cell(200, 5, txt="Frameworks & Tools: React, Spring Boot, Git, Docker", ln=1)
    pdf.cell(200, 5, txt="Soft Skills: Communication, Presentation, Teamwork, Agile", ln=1)
    pdf.ln(5)
    
    # Projects section
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Projects", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, txt="1. AI Attendance System: Built using Python and OpenCV for facial recognition.\n"
                           "2. Portfolio Website: Developed an interactive responsive site using React and Tailwind.")
    pdf.ln(5)
    
    # Work Experience
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Work Experience", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt="Software Engineer Intern at Technosoft Systems (2 months)", ln=1)
    pdf.ln(5)
    
    # Certifications
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Certifications", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt="- AWS Certified Solutions Architect - Associate", ln=1)
    
    pdf.output(output_path)
    print(f"Generated dummy resume PDF at: {output_path}")

def run_pipeline():
    print("==================================================")
    print("STARTING END-TO-END CORE ML PIPELINE INTEGRATION TEST")
    print("==================================================")
    
    # 1. Setup paths
    dummy_pdf_path = "data/dummy_resume.pdf"
    generate_dummy_resume_pdf(dummy_pdf_path)
    
    # Mock job description text
    mock_jd = """
    We are seeking a Backend Developer.
    Required Skills: Python, SQL, Java, Spring Boot, Git, Docker, Kubernetes.
    Preferred: AWS experience, Teamwork, Agile.
    """
    print(f"\nTarget Job Description:\n{mock_jd.strip()}")
    
    # 2. Parse Resume PDF
    print("\n--- Step 1: Parsing Resume PDF ---")
    parsed_resume = parse_resume_pdf(dummy_pdf_path)
    print(f"Extracted Specialization: {parsed_resume['features']['specialization']}")
    print(f"Extracted CGPA: {parsed_resume['features']['CGPA']}")
    print(f"Extracted Skills count: {len(parsed_resume['skills'])}")
    
    # 3. Parse Job Description Text
    print("\n--- Step 2: Parsing Job Description ---")
    parsed_jd = parse_job_description(mock_jd)
    print(f"Extracted JD Skills: {parsed_jd['skills']}")
    
    # 4. Predict Placement Readiness & Explain via SHAP
    print("\n--- Step 3: Running ML Placement Predictor & SHAP Explainability ---")
    student_features_df = pd.DataFrame([parsed_resume['features']])
    
    # Run explainability engine which evaluates the model internally
    model_dir = "models"
    explanation = explain_student_readiness(student_features_df, models_dir=model_dir)
    
    print(f"Placement Readiness Probability: {explanation['readiness_probability'] * 100:.2f}%")
    print(f"Model Base Probability: {explanation['base_probability'] * 100:.2f}%")
    
    # 5. Run Skill Gap Engine
    print("\n--- Step 4: Analyzing Skill Gap (Semantic Similarity Matcher) ---")
    gap_analysis = analyze_skill_gap(parsed_resume['skills'], parsed_jd['skills'])
    print(f"Matched Skills count: {len(gap_analysis['matched'])}")
    print(f"Partially Matched count: {len(gap_analysis['partially_matched'])}")
    print(f"Missing Skills count: {len(gap_analysis['missing'])}")
    
    # 6. Consolidate Outputs
    pipeline_output = {
        "student_profile": {
            "name": "Siddharth Sharma",
            "features": parsed_resume["features"],
            "resume_skills": parsed_resume["skills"]
        },
        "job_profile": {
            "required_skills": parsed_jd["skills"]
        },
        "readiness_analysis": {
            "placement_readiness_score": round(explanation["readiness_probability"] * 100, 2),
            "shap_explanation": {
                "base_probability": round(explanation["base_probability"] * 100, 2),
                "contributions": explanation["contributions"]
            }
        },
        "skill_gap_analysis": gap_analysis
    }
    
    # Save the consolidated output JSON
    output_json_path = "data/pipeline_output.json"
    with open(output_json_path, 'w') as f:
        json.dump(pipeline_output, f, indent=2)
        
    print("\n==================================================")
    print(f"PIPELINE RUN COMPLETED SUCCESSFULY! SAVED TO: {output_json_path}")
    print("==================================================")
    
    # Print a clean, formatted sample of the output JSON
    print(json.dumps(pipeline_output, indent=2))

if __name__ == "__main__":
    run_pipeline()
