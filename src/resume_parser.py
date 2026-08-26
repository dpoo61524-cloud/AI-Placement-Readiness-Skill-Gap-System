import os
import re
import json

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
except Exception as e:
    nlp = None

# Comprehensive Multi-Domain Technology & Skill Knowledge Base
SKILL_DICTIONARY = {
    # Programming Languages
    "python": ["python", "py"],
    "java": ["java"],
    "c++": ["c\\+\\+", "cpp"],
    "c": ["\\bc\\b"],
    "c#": ["c#", "c-sharp", "csharp"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "ruby": ["ruby", "rails"],
    "go": ["golang", "\\bgo\\b"],
    "php": ["php"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "sql": ["sql", "mysql", "postgresql", "sqlite", "oracle sql", "pl/sql", "t-sql", "nosql"],
    "rust": ["rust"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "r": ["\\br\\b", "r-lang", "r language"],
    "scala": ["scala"],
    "matlab": ["matlab"],
    "bash": ["bash", "shell scripting", "shell"],
    
    # Frameworks & Libraries
    "react": ["react", "react\\.js", "reactjs", "react-native", "react native"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vue\\.js", "vuejs"],
    "django": ["django"],
    "flask": ["flask"],
    "node.js": ["node", "node\\.js", "nodejs"],
    "express": ["express", "express\\.js", "expressjs"],
    "spring boot": ["spring boot", "spring", "spring mvc"],
    "fastapi": ["fastapi"],
    "bootstrap": ["bootstrap"],
    "tailwind": ["tailwind", "tailwindcss"],
    "next.js": ["next", "next\\.js", "nextjs"],
    "jquery": ["jquery"],
    "graphql": ["graphql"],
    "redux": ["redux"],
    
    # Machine Learning, AI & Data Science
    "numpy": ["numpy"],
    "pandas": ["pandas"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "opencv": ["opencv"],
    "nlp": ["nlp", "natural language processing", "spacy", "nltk", "text mining"],
    "llm": ["llm", "large language model", "gpt", "bert", "transformers", "langchain", "huggingface", "rag"],
    "powerbi": ["powerbi", "power bi", "power-bi"],
    "tableau": ["tableau"],
    "spark": ["spark", "pyspark", "apache spark"],
    "scipy": ["scipy"],
    "excel": ["excel", "excle", "ms excel", "ms-excel", "microsoft excel", "spreadsheets", "advanced excel", "vlookup", "pivot tables"],
    "snowflake": ["snowflake"],
    "bigquery": ["bigquery", "bq"],
    "hadoop": ["hadoop", "hdfs", "hive"],
    "airflow": ["airflow", "apache airflow"],
    "kafka": ["kafka", "apache kafka"],
    
    # Databases
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "firebase": ["firebase"],
    "dynamodb": ["dynamodb"],
    "oracle": ["oracle"],
    "cassandra": ["cassandra"],
    "neo4j": ["neo4j"],
    
    # Tools, Cloud & DevOps
    "git": ["git", "github", "gitlab", "bitbucket"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "rds", "cloudformation"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "azure": ["azure", "microsoft azure"],
    "jenkins": ["jenkins"],
    "ci/cd": ["ci/cd", "continuous integration", "github actions", "gitlab ci"],
    "linux": ["linux", "ubuntu", "centos", "redhat", "unix"],
    "terraform": ["terraform"],
    
    # Testing & Automation
    "playwright": ["playwright"],
    "selenium": ["selenium", "selenium webdriver"],
    "cypress": ["cypress"],
    "postman": ["postman", "api testing", "rest api testing"],
    "rest api": ["rest api", "restful", "rest apis", "web apis", "microservices"],
    "jmeter": ["jmeter"],
    "pytest": ["pytest"],
    "junit": ["junit"],
    "jira": ["jira"],
    
    # Soft Skills
    "communication": ["communication", "verbal communication", "written communication", "interpersonal"],
    "leadership": ["leadership", "team lead", "mentoring", "managed"],
    "teamwork": ["teamwork", "collaboration", "team player"],
    "presentation": ["presentation", "public speaking"],
    "agile": ["agile", "scrum", "kanban"],
    "problem solving": ["problem solving", "analytical skills", "critical thinking"]
}

def extract_raw_text_from_pdf(pdf_path):
    text = ""
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_skills(text):
    extracted_skills = []
    text_lower = text.lower()
    
    for skill_name, patterns in SKILL_DICTIONARY.items():
        for pattern in patterns:
            if "\\b" in pattern:
                match = re.search(pattern, text_lower)
            else:
                start_boundary = r'\b' if pattern[0].isalnum() or pattern[0] == '_' else ''
                end_boundary = r'\b' if pattern[-1].isalnum() or pattern[-1] == '_' else ''
                match = re.search(start_boundary + re.escape(pattern) + end_boundary, text_lower)
                
            if match:
                extracted_skills.append(skill_name)
                break
                
    return list(set(extracted_skills))

def extract_cgpa(text):
    cgpa_keywords = r"(?:cgpa|gpa|pointer|sgpa|g\.p\.a|c\.g\.p\.a|marks|aggregate|grade)"
    cgpa_pattern = r"\b([5-9]\.\d{1,2}|10\.0)\b"
    
    # 1. 10.0 scale: 8.5/10, 8.5 out of 10
    out_of_10_match = re.search(r"\b([5-9]\.\d{1,2}|10\.0)\s*(?:\/|\bout\s+of\b)\s*10\b", text, re.IGNORECASE)
    if out_of_10_match:
        return float(out_of_10_match.group(1))
        
    # 2. 4.0 scale: 3.8/4.0 -> convert to 10 scale (multiply by 2.5)
    out_of_4_match = re.search(r"\b([2-3]\.\d{1,2}|4\.0)\s*(?:\/|\bout\s+of\b)\s*4(?:\.0)?\b", text, re.IGNORECASE)
    if out_of_4_match:
        return round(float(out_of_4_match.group(1)) * 2.5, 2)

    # 3. Explicit percentages like 85% or 75.5%
    pct_match = re.search(r"\b(\d{2}(?:\.\d+)?)\s*%", text)
    if pct_match:
        pct_val = float(pct_match.group(1))
        if 55.0 <= pct_val <= 100.0:
            return round(pct_val / 10.0, 2)

    # 4. Pattern like CGPA: 8.5
    matches = re.findall(rf"{cgpa_keywords}.*?{cgpa_pattern}", text, re.IGNORECASE)
    if matches:
        return float(matches[0])
        
    # 5. Fallback float search
    floats = re.findall(cgpa_pattern, text)
    if floats:
        for f in sorted(floats, key=float, reverse=True):
            val = float(f)
            if 5.5 <= val <= 10.0:
                if re.search(cgpa_keywords, text, re.IGNORECASE):
                    return val
                    
    return 7.5

def extract_backlogs(text):
    text_lower = text.lower()
    if re.search(r"\bno\s+backlog\b|\bzero\s+backlog\b|\bno\s+arrear\b|\b0\s+backlog\b|\bcleared\s+all\b", text_lower):
        return 0
    match = re.search(r"(\d+)\s*(?:active\s*)?(?:backlog|arrear)", text_lower)
    if match:
        return int(match.group(1))
    return 0

def extract_sections(text):
    headers = [
        "OBJECTIVE", "SUMMARY", "PROFILE", "PROFESSIONAL SUMMARY", "EXECUTIVE SUMMARY",
        "EDUCATION", "ACADEMIC BACKGROUND", "ACADEMIC QUALIFICATIONS", "SCHOLASTIC RECORD",
        "TECHNICAL SKILLS", "SKILLS", "SKILL HIGHLIGHTS", "TECH STACK", "AREAS OF EXPERTISE", "CORE COMPETENCIES",
        "INTERNSHIP EXPERIENCE", "WORK EXPERIENCE", "EXPERIENCE", "EMPLOYMENT HISTORY", "CAREER HISTORY", "INTERNSHIPS", "INDUSTRIAL TRAINING",
        "PROJECTS", "PERSONAL PROJECTS", "ACADEMIC PROJECTS", "KEY PROJECTS", "PORTFOLIO",
        "CERTIFICATIONS", "CERTIFICATES", "COURSES & CERTIFICATIONS", "LICENSES & CERTIFICATIONS", "ACCOMPLISHMENTS",
        "LEADERSHIP & ACTIVITIES", "LEADERSHIP", "ACTIVITIES", "EXTRACURRICULAR ACTIVITIES", "ACHIEVEMENTS"
    ]
    
    lines = text.split('\n')
    sections = {}
    current_section = "HEADER"
    sections[current_section] = []
    
    for line in lines:
        clean_line = line.strip()
        match = re.match(r'^[ \t]*(' + '|'.join(headers) + r'):?[ \t]*$', clean_line, re.IGNORECASE)
        if match:
            current_section = match.group(1).upper()
            sections[current_section] = []
        else:
            sections.get(current_section, []).append(line)
            
    return {sec: "\n".join(content).strip() for sec, content in sections.items()}

def extract_internships_count(text, sections=None):
    if sections is None:
        sections = extract_sections(text)
        
    intern_text = (
        sections.get("INTERNSHIP EXPERIENCE", "") + "\n" + 
        sections.get("INTERNSHIPS", "") + "\n" + 
        sections.get("INDUSTRIAL TRAINING", "") + "\n" + 
        sections.get("WORK EXPERIENCE", "") + "\n" + 
        sections.get("EXPERIENCE", "") + "\n" + 
        sections.get("EMPLOYMENT HISTORY", "")
    ).strip()
    
    if intern_text:
        # Match distinct job/internship title headers or company lines
        header_entries = []
        for line in intern_text.split('\n'):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith(('-', '*', '•', '●', '1.', '2.', '3.', '4.', '5.')):
                continue
            if re.search(r"\b(intern|internship|trainee|apprentice|co-op|coop|developer|engineer|analyst|associate)\b", line_clean, re.IGNORECASE):
                header_entries.append(line_clean)
        if header_entries:
            return min(len(header_entries), 5)
            
    text_lower = text.lower()
    
    # Check date range indicators (e.g. May 2023 - Jul 2023, 06/2022 to 08/2022, 2 months)
    date_ranges = len(re.findall(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{1,2}/\d{4}|\d{4})\s*(?:-|to|–)\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present|current|\d{1,2}/\d{4}|\d{4})\b", text_lower))
    intern_matches = len(re.findall(r"\b(?:intern|internship|trainee|co-op|coop|apprentice)\b", text_lower))
    
    count = max(intern_matches // 2, date_ranges)
    if count == 0 and intern_matches > 0:
        count = 1
        
    return min(max(count, 0), 5)

def extract_projects_count(text, sections=None):
    if sections is None:
        sections = extract_sections(text)
        
    proj_text = (
        sections.get("PROJECTS", "") + "\n" + 
        sections.get("KEY PROJECTS", "") + "\n" + 
        sections.get("ACADEMIC PROJECTS", "") + "\n" + 
        sections.get("PERSONAL PROJECTS", "") + "\n" + 
        sections.get("PORTFOLIO", "")
    ).strip()
    
    if proj_text:
        proj_titles = [line.strip() for line in proj_text.split('\n') if line.strip() and not line.strip().startswith(('●', '-', '•', '*', '1.', '2.'))]
        if proj_titles:
            return min(max(len(proj_titles), 1), 5)
            
    text_lower = text.lower()
    lines = text_lower.split('\n')
    project_indicators = 0
    for line in lines:
        if re.search(r"\b(?:github\.com|gitlab\.com|bitbucket\.org)\b", line):
            project_indicators += 1
        elif re.search(r"\b(?:developed|built|implemented|created|designed|engineered)\b", line):
            project_indicators += 1
            
    enum_matches = len(re.findall(r"\b(?:project\s+\d|\b\d\.\s+[a-z]+)\b", text_lower))
    project_indicators = max(project_indicators, enum_matches)
    
    if project_indicators == 0:
        project_indicators = len(re.findall(r"\bprojects?\b", text_lower))
        
    return min(max(project_indicators, 0), 5)

def extract_certifications_count(text, sections=None):
    if sections is None:
        sections = extract_sections(text)
        
    cert_text = (
        sections.get("CERTIFICATIONS", "") + "\n" + 
        sections.get("CERTIFICATES", "") + "\n" + 
        sections.get("COURSES & CERTIFICATIONS", "") + "\n" + 
        sections.get("LICENSES & CERTIFICATIONS", "") + "\n" + 
        sections.get("ACCOMPLISHMENTS", "")
    ).strip()
    
    raw_certs = [c.strip() for c in re.split(r'[•\n|\u2022;,]', cert_text) if len(c.strip()) > 3]
    if raw_certs:
        return min(len(raw_certs), 10)
        
    text_lower = text.lower()
    keywords = r"\b(?:certified|certification|certifications|certificate|certificates|coursera|udemy|nptel|credential|credentials|badge|badges|license|licenses|course|courses|nanodegree|edx|hackerrank|pluralsight|bootcamp)\b"
    cert_matches = len(re.findall(keywords, text_lower))
    providers = r"\b(?:aws|gcp|azure|google\s+cloud|microsoft|oracle|ibm|red\s+hat|cisco|comptia|salesforce|freecodecamp|scrum|pmp|udacity)\b"
    provider_matches = len(re.findall(providers, text_lower))
    
    total = max(cert_matches, provider_matches)
    return min(max(total, 0), 10)

def extract_specialization(text):
    text_lower = text.lower()
    if re.search(r"\bdata\s+analytics?\b|\bdata\s+science\b|\bdata\s+analyst\b|\bdata\s+engineering\b|\bbig\s+data\b|\bbusiness\s+analytics?\b", text_lower):
        return "Data Analytics"
    elif re.search(r"\bartificial\s+intelligence\b|\bmachine\s+learning\b|\bai\s*&\s*ml\b|\bai/ml\b", text_lower):
        return "Artificial Intelligence"
    elif re.search(r"\bcomputer\s+science\b|\bcse\b|\bsoftware\s+engineering\b|\bcomputer\s+engineering\b|\bmca\b|\bbca\b", text_lower):
        return "Computer Science"
    elif re.search(r"\binformation\s+technology\b|\bit\b|\binformation\s+science\b", text_lower):
        return "Information Technology"
    elif re.search(r"\belectronics\b|\bece\b|\beee\b|\btelecommunication\b|\bcommunication\s+engineering\b", text_lower):
        return "Electronics"
    elif re.search(r"\bmechanical\b|\bme\b|\brobotics\b", text_lower):
        return "Mechanical"
    elif re.search(r"\bcivil\b|\bce\b|\bconstruction\b", text_lower):
        return "Civil"
    return "Computer Science"

def parse_resume_text(text):
    sections = extract_sections(text)
    skills = extract_skills(text)
    cgpa = extract_cgpa(text)
    backlogs = extract_backlogs(text)
    internships = extract_internships_count(text, sections=sections)
    projects = extract_projects_count(text, sections=sections)
    certifications = extract_certifications_count(text, sections=sections)
    specialization = extract_specialization(text)
    
    # Coding Score heuristic
    coding_skills = ["python", "java", "c++", "c", "c#", "javascript", "typescript", "go", "rust", "sql", "r", "scala", "playwright", "selenium", "react", "spring boot", "node.js"]
    student_coding_skills = [s for s in skills if s in coding_skills]
    
    base_coding = 45.0 + 4.0 * (cgpa - 6.0) + 5.0 * projects + len(student_coding_skills) * 3.5
    coding_score = float(min(max(base_coding, 25.0), 98.0))
    
    # Communication Score heuristic
    soft_skills = ["communication", "leadership", "teamwork", "presentation", "agile", "problem solving"]
    student_soft_skills = [s for s in skills if s in soft_skills]
    
    base_comm = 55.0 + 3.0 * internships + 4.0 * len(student_soft_skills)
    communication_score = float(min(max(base_comm, 40.0), 95.0))
    
    return {
        "features": {
            "CGPA": cgpa,
            "backlogs": backlogs,
            "internships": internships,
            "projects": projects,
            "certifications": certifications,
            "coding_score": round(coding_score, 1),
            "communication_score": round(communication_score, 1),
            "specialization": specialization
        },
        "skills": skills
    }

def parse_job_description(jd_text):
    skills = extract_skills(jd_text)
    return {
        "skills": skills
    }

def parse_resume_pdf(pdf_path):
    text = extract_raw_text_from_pdf(pdf_path)
    parsed = parse_resume_text(text)
    parsed["raw_text"] = text
    return parsed
