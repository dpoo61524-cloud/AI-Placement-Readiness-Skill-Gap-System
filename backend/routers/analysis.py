import os
import sys
import io
import json
import hashlib
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Add workspace root directory to path dynamically to prevent import errors
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Local ML & parser modules
from src.resume_parser import parse_resume_text, parse_job_description, extract_raw_text_from_pdf
from src.explain import explain_student_readiness
from src.skill_gap import analyze_skill_gap
from src.recommendation import assemble_4_week_plan
from src.groq_enhance import enhance_plan_with_llm


# Database connectivity
from backend.db.session import get_db
from backend.db.models import SubmissionCache

# Validation Schemas
from backend import schemas

router = APIRouter()

@router.post("/parse-resume", response_model=schemas.StudentProfile)
def parse_resume(file: UploadFile = File(...)):
    """
    Accepts student resume PDF upload and returns parsed features & skills.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a PDF resume."
        )
        
    try:
        # Extract text directly from memory stream bytes
        file_bytes = file.file.read()
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract any text from the uploaded PDF resume."
            )
            
        parsed = parse_resume_text(text)
        return {
            "features": parsed["features"],
            "resume_skills": parsed["skills"]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing resume PDF: {str(e)}"
        )

@router.post("/predict", response_model=schemas.PredictResponse)
def predict_readiness(features: schemas.StudentFeatures):
    """
    Accepts student features and returns eligibility prediction probability + SHAP values.
    """
    try:
        # Convert Pydantic features to DataFrame for ML model
        features_df = pd.DataFrame([features.dict()])
        # Run explainability module
        explanation = explain_student_readiness(features_df, models_dir="models")
        return explanation
    except FileNotFoundError as fnf:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model files not loaded on backend server: {str(fnf)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction server error: {str(e)}"
        )

@router.post("/skill-gap", response_model=schemas.SkillGapResponse)
def compute_skill_gap(request: schemas.SkillGapRequest):
    """
    Accepts student skills list and Job Description text, runs similarity matches, and weights missing skills.
    """
    try:
        parsed_jd = parse_job_description(request.job_description)
        gap_report = analyze_skill_gap(request.resume_skills, parsed_jd["skills"])
        return gap_report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skill gap engine failed: {str(e)}"
        )

@router.post("/recommendations", response_model=schemas.RecommendationsResponse)
def fetch_recommendations(request: schemas.RecommendationsRequest):
    """
    Accepts missing skills and student CGPA, runs RAG index retrieval, and returns the 4-week timeline.
    """
    try:
        plan = assemble_4_week_plan(request.missing_skills, student_cgpa=request.student_cgpa)
        enhanced_plan = enhance_plan_with_llm(plan)
        return enhanced_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation engine failed: {str(e)}"
        )

@router.post("/full-analysis", response_model=schemas.FullAnalysisResponse)
def run_full_analysis(
    resume: UploadFile = File(...), 
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Orchestrates parse -> predict -> gap -> recommend in one call with SQLite caching.
    Uses SHA256 of (resume bytes + job description text) as cache key.
    """
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Resume must be a PDF."
        )
        
    if not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job Description text cannot be empty."
        )
        
    try:
        # Read file bytes
        resume_bytes = resume.file.read()
        
        # Compute SHA256 input hash
        hash_input = resume_bytes + job_description.encode('utf-8')
        input_hash = hashlib.sha256(hash_input).hexdigest()
        
        # 1. Check database cache
        cached_record = db.query(SubmissionCache).filter(SubmissionCache.input_hash == input_hash).first()
        if cached_record:
            print(f"Cache Hit! Returning cached result for hash: {input_hash}")
            return json.loads(cached_record.result_json)
            
        print(f"Cache Miss! Running full analysis pipeline for hash: {input_hash}")
        
        # 2. Pipeline Execution
        # Extract text from resume PDF
        text = ""
        import pdfplumber
        with pdfplumber.open(io.BytesIO(resume_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Resume PDF does not contain indexable text."
            )
            
        # Parse resume text
        parsed_resume = parse_resume_text(text)
        
        # Model predictions & SHAP explanations
        student_features = parsed_resume["features"]
        student_features_df = pd.DataFrame([student_features])
        explanation = explain_student_readiness(student_features_df, models_dir="models")
        
        # Parse Job Description skills
        parsed_jd = parse_job_description(job_description)
        
        # Analyze skill gaps
        gap_report = analyze_skill_gap(parsed_resume["skills"], parsed_jd["skills"])
        
        # Calculate skill match ratio to calibrate placement readiness score based on job description alignment
        base_probability = explanation["readiness_probability"]
        total_weight = 0
        matched_weight = 0.0
        
        for item in gap_report["matched"]:
            w = item["importance_weight"]
            total_weight += w
            matched_weight += w * item["similarity_score"]
            
        for item in gap_report["partially_matched"]:
            w = item["importance_weight"]
            total_weight += w
            matched_weight += w * item["similarity_score"]
            
        for item in gap_report["missing"]:
            w = item["importance_weight"]
            total_weight += w
            
        if total_weight > 0:
            skill_ratio = matched_weight / total_weight
            # 30% general model eligibility + 70% job-specific skill match
            calibrated_probability = (0.3 * base_probability) + (0.7 * base_probability * skill_ratio)
        else:
            calibrated_probability = base_probability
            
        calibrated_probability = min(max(calibrated_probability, 0.0), 1.0)
        
        # Assemble RAG recommendations
        missing_skills_mapped = [
            {"required_skill": s["required_skill"], "importance_weight": s["importance_weight"]}
            for s in gap_report["missing"]
        ]
        recommendations = assemble_4_week_plan(missing_skills_mapped, student_cgpa=student_features["CGPA"])
        enhanced_recommendations = enhance_plan_with_llm(recommendations)
        
        # Consolidate response
        full_analysis_output = {
            "student_profile": {
                "features": student_features,
                "resume_skills": parsed_resume["skills"]
            },
            "job_profile": {
                "required_skills": parsed_jd["skills"]
            },
            "readiness_analysis": {
                "placement_readiness_score": round(calibrated_probability * 100, 2),
                "shap_explanation": {
                    "base_probability": round(explanation["base_probability"] * 100, 2),
                    "contributions": explanation["contributions"]
                }
            },
            "skill_gap_analysis": gap_report,
            "recommendation_plan": enhanced_recommendations
        }
        
        # 3. Save to database cache
        cache_entry = SubmissionCache(
            input_hash=input_hash,
            timestamp=datetime.utcnow(),
            resume_filename=resume.filename,
            result_json=json.dumps(full_analysis_output)
        )
        db.add(cache_entry)
        db.commit()
        
        return full_analysis_output
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Full-analysis pipeline failed: {str(e)}"
        )

@router.get("/history", response_model=List[schemas.HistoryItem])
def get_submission_history(db: Session = Depends(get_db)):
    """
    Returns list of past submissions stored in SQLite cache database.
    """
    try:
        records = db.query(SubmissionCache).order_by(SubmissionCache.timestamp.desc()).all()
        history = []
        for r in records:
            history.append({
                "input_hash": r.input_hash,
                "timestamp": r.timestamp,
                "resume_filename": r.resume_filename,
                "result": json.loads(r.result_json)
            })
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch submission history: {str(e)}"
        )
