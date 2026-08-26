import os
import json
import numpy as np
from difflib import SequenceMatcher

model = None
SENTENCE_TRANSFORMERS_AVAILABLE = True

# Fallback similarity function
def calculate_string_similarity(str1, str2):
    """
    Computes a text-based similarity score [0, 1] using SequenceMatcher and substring rules.
    """
    s1, s2 = str1.lower().strip(), str2.lower().strip()
    
    # Exact match
    if s1 == s2:
        return 1.0
        
    # Substring matches (e.g. "react.js" and "react", "node.js" and "node")
    if s1 in s2 or s2 in s1:
        # Check if they are very close, e.g. "react" in "reactjs" is highly similar
        len_ratio = min(len(s1), len(s2)) / max(len(s1), len(s2))
        if len_ratio > 0.4:
            return 0.85 + (0.15 * len_ratio)
            
    # SequenceMatcher ratio
    ratio = SequenceMatcher(None, s1, s2).ratio()
    
    # Common abbreviation matching
    abbreviations = {
        "js": "javascript",
        "ts": "typescript",
        "cpp": "c++",
        "py": "python",
        "nlp": "natural language processing",
        "excle": "excel",
        "ms excel": "excel",
        "microsoft excel": "excel"
    }
    if abbreviations.get(s1) == s2 or abbreviations.get(s2) == s1:
        return 0.95
        
    return ratio

def get_cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    return dot_product / (norm_vec1 * norm_vec2)

def compute_semantic_similarities(resume_skills, jd_skills):
    """
    Computes the similarity matrix between resume_skills and jd_skills.
    Returns a dict mapping each jd_skill to a tuple: (best_matching_student_skill, similarity_score)
    """
    global model, SENTENCE_TRANSFORMERS_AVAILABLE
    
    results = {}
    
    # If no resume skills, all similarities are 0
    if not resume_skills:
        for jd_skill in jd_skills:
            results[jd_skill] = (None, 0.0)
        return results
        
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            if model is None:
                print("Loading SentenceTransformer 'all-MiniLM-L6-v2'...", flush=True)
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Embed all skills
            resume_embeddings = model.encode(resume_skills)
            jd_embeddings = model.encode(jd_skills)
            
            for i, jd_skill in enumerate(jd_skills):
                jd_emb = jd_embeddings[i]
                best_sim = -1.0
                best_skill = None
                
                for j, res_skill in enumerate(resume_skills):
                    res_emb = resume_embeddings[j]
                    sim = float(get_cosine_similarity(jd_emb, res_emb))
                    
                    if sim > best_sim:
                        best_sim = sim
                        best_skill = res_skill
                        
                results[jd_skill] = (best_skill, best_sim)
                
            return results
        except Exception as e:
            print(f"Error running SentenceTransformer: {str(e)}. Falling back to string similarity.")
            
    # Fallback to pure string matching
    for jd_skill in jd_skills:
        best_sim = -1.0
        best_skill = None
        for res_skill in resume_skills:
            sim = calculate_string_similarity(jd_skill, res_skill)
            if sim > best_sim:
                best_sim = sim
                best_skill = res_skill
        results[jd_skill] = (best_skill, best_sim)
        
    return results

def generate_skill_importance(output_path="data/skill_importance.json"):
    """
    Generates a frequency-based skill importance dictionary from mock job descriptions
    and saves it to a JSON file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 15 Reference Job Descriptions represented as sets of skills
    reference_jds = [
        {"python", "django", "postgresql", "redis", "docker", "git", "aws"},
        {"javascript", "typescript", "react", "html", "css", "bootstrap", "git"},
        {"javascript", "react", "node.js", "express", "mongodb", "git", "aws", "communication"},
        {"python", "pandas", "numpy", "scikit-learn", "tensorflow", "sql", "tableau", "communication"},
        {"linux", "docker", "kubernetes", "aws", "jenkins", "ci/cd", "git", "agile"},
        {"python", "java", "git", "communication", "agile"},
        {"java", "spring boot", "sql", "git", "docker", "aws", "teamwork"},
        {"kotlin", "firebase", "git", "teamwork"},
        {"python", "sql", "pandas", "aws", "git"},
        {"html", "css", "bootstrap", "tailwind", "javascript"},
        {"aws", "azure", "docker", "kubernetes", "linux", "communication"},
        {"c++", "linux", "git", "teamwork"},
        {"python", "pytorch", "tensorflow", "numpy", "pandas", "git", "docker", "aws"},
        {"agile", "communication", "leadership", "presentation", "teamwork"},
        {"sql", "powerbi", "tableau", "presentation", "communication", "teamwork"}
    ]
    
    # Count frequencies
    frequencies = {}
    for jd in reference_jds:
        for skill in jd:
            frequencies[skill] = frequencies.get(skill, 0) + 1
            
    # Normalize frequencies to a 1-5 weight scale
    # Map frequency counts to weights
    skill_importance = {}
    for skill, count in frequencies.items():
        if count >= 7:
            weight = 5
        elif count >= 5:
            weight = 4
        elif count >= 3:
            weight = 3
        elif count >= 2:
            weight = 2
        else:
            weight = 1
        skill_importance[skill] = weight
        
    with open(output_path, 'w') as f:
        json.dump(skill_importance, f, indent=2)
        
    print(f"Skill importance database saved to {output_path}")
    return skill_importance

def load_skill_importance(path="data/skill_importance.json"):
    if not os.path.exists(path):
        return generate_skill_importance(path)
        
    with open(path, 'r') as f:
        return json.load(f)

def analyze_skill_gap(resume_skills, jd_skills, importance_path="data/skill_importance.json"):
    """
    Compares student skills against job description skills and outputs the gap report.
    """
    importance_dict = load_skill_importance(importance_path)
    similarities = compute_semantic_similarities(resume_skills, jd_skills)
    
    matched_skills = []
    partially_matched_skills = []
    missing_skills = []
    
    for jd_skill, (best_res_skill, score) in similarities.items():
        # Retrieve importance weight, defaulting to 2 (Low-Medium) for unknown skills
        weight = importance_dict.get(jd_skill.lower(), 2)
        
        skill_info = {
            "required_skill": jd_skill,
            "matched_student_skill": best_res_skill,
            "similarity_score": round(score, 2),
            "importance_weight": weight
        }
        
        if score >= 0.85:
            matched_skills.append(skill_info)
        elif score >= 0.50:
            partially_matched_skills.append(skill_info)
        else:
            skill_info["matched_student_skill"] = None
            skill_info["similarity_score"] = 0.0
            missing_skills.append(skill_info)
            
    # Sort missing skills by importance weight (highest first)
    missing_skills.sort(key=lambda x: x["importance_weight"], reverse=True)
    
    return {
        "matched": matched_skills,
        "partially_matched": partially_matched_skills,
        "missing": missing_skills
    }

if __name__ == "__main__":
    # Generate database
    generate_skill_importance()
    
    # Test gap analysis
    student = ["python", "react", "django", "git", "communication"]
    job = ["python", "react.js", "docker", "teamwork", "postgres"]
    
    print("\nRunning test gap analysis...")
    gap_report = analyze_skill_gap(student, job)
    
    print("\nMatched:")
    for s in gap_report["matched"]:
        print(f"  {s['required_skill']} matched with student's {s['matched_student_skill']} (Score: {s['similarity_score']})")
        
    print("\nPartially Matched:")
    for s in gap_report["partially_matched"]:
        print(f"  {s['required_skill']} partially matched with student's {s['matched_student_skill']} (Score: {s['similarity_score']})")
        
    print("\nMissing (ordered by importance):")
    for s in gap_report["missing"]:
        print(f"  {s['required_skill']} (Importance Weight: {s['importance_weight']})")
