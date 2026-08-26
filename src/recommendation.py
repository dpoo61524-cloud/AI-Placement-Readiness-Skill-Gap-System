import os
import json
import numpy as np
import faiss

# Lazy-loaded globals to save startup memory and time
model = None
faiss_index = None
learning_resources = []
resource_embeddings = None

def load_resources_db(path="data/learning_resources.json"):
    """
    Loads learning resources list from JSON.
    """
    global learning_resources
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resource database not found at {path}")
    with open(path, 'r') as f:
        learning_resources = json.load(f)
    return learning_resources

def initialize_rag_index(resources_path="data/learning_resources.json"):
    """
    Embeds resources and initializes the FAISS Index in memory.
    """
    global model, faiss_index, learning_resources, resource_embeddings
    
    if len(learning_resources) == 0:
        load_resources_db(resources_path)
        
    if model is None:
        print("RAG: Loading SentenceTransformer 'all-MiniLM-L6-v2'...", flush=True)
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
    print(f"RAG: Indexing {len(learning_resources)} resources into FAISS...")
    
    # Formulate a descriptive text representation for each resource to embed
    texts_to_embed = [
        f"{r['title']} - {r['description']} (Skill: {r['skill_tag']}, Type: {r['resource_type']})"
        for r in learning_resources
    ]
    
    # Generate embeddings
    embeddings = model.encode(texts_to_embed)
    resource_embeddings = np.array(embeddings).astype('float32')
    
    # Setup FAISS
    dimension = resource_embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(resource_embeddings)
    
    print("RAG: FAISS Vector Index initialized successfully.")

def retrieve_resources_for_skill(skill_tag, top_k=5, resources_path="data/learning_resources.json"):
    """
    Retrieves resources for a skill using a hybrid approach:
    1. Exact matches for the skill_tag.
    2. Semantic RAG fallback/expansion using FAISS vector search.
    """
    global faiss_index, learning_resources, model
    
    if len(learning_resources) == 0:
        load_resources_db(resources_path)
        
    skill_lower = skill_tag.lower().strip()
    
    # Normalize common skill aliases (e.g., excle -> excel)
    alias_map = {
        "excle": "excel",
        "ms-excel": "excel",
        "ms excel": "excel",
        "microsoft excel": "excel",
        "comm": "communication",
        "soft skills": "communication",
        "soft skill": "communication",
        "r-lang": "r",
        "r language": "r"
    }
    skill_lower = alias_map.get(skill_lower, skill_lower)
    
    # 1. Exact match extraction
    exact_matches = [r for r in learning_resources if r['skill_tag'].lower() == skill_lower]
    
    if len(exact_matches) >= top_k:
        return exact_matches[:top_k]
    elif len(exact_matches) > 0:
        return exact_matches
        
    # Ensure RAG is initialized for vector search fallback
    if faiss_index is None:
        try:
            initialize_rag_index(resources_path)
        except Exception as e:
            print(f"RAG index initialization skipped: {e}")
            return exact_matches
            
    if model is not None and faiss_index is not None:
        query_text = f"Study resources courses tutorial for {skill_tag}"
        query_vector = model.encode([query_text]).astype('float32')
        
        distances, indices = faiss_index.search(query_vector, 15)
        
        semantic_matches = []
        seen_titles = {r['title'] for r in exact_matches}
        
        for idx in indices[0]:
            if idx < 0 or idx >= len(learning_resources):
                continue
            res = learning_resources[idx]
            if res['title'] not in seen_titles and (res['skill_tag'].lower() == skill_lower or skill_lower in res['title'].lower() or skill_lower in res['description'].lower()):
                semantic_matches.append(res)
                seen_titles.add(res['title'])
                
        combined = exact_matches + semantic_matches
        if combined:
            return combined[:top_k]
            
    return exact_matches[:top_k]

def generate_domain_project(skill, difficulty):
    s = (skill or "").lower().strip()
    if s in ["communication", "presentation", "leadership", "teamwork"]:
        return {
            "title": "Corporate Communication & Executive Presentation Portfolio",
            "provider": "Self-Guided Professional Project",
            "difficulty": difficulty,
            "description": "Develop a comprehensive professional communication portfolio including executive proposals, slide decks, and technical project presentation walkthroughs.",
            "link": "https://github.com/topics/presentation-deck",
            "skill_tag": "communication",
            "resource_type": "project_idea"
        }
    elif s in ["java", "java se", "java developer", "java programming"]:
        return {
            "title": "Enterprise Java SE Data Analytics & Management System",
            "provider": "Self-Guided Software Project",
            "difficulty": difficulty,
            "description": "Develop a modular Java SE application utilizing OOP principles, collections framework, JDBC database connectivity, and automated Excel data reporting export.",
            "link": "https://github.com/topics/java-project",
            "skill_tag": "java",
            "resource_type": "project_idea"
        }
    elif s in ["excel", "excle", "ms excel", "spreadsheets"]:
        return {
            "title": "Executive Financial & Sales Analytics Dashboard in Microsoft Excel",
            "provider": "Self-Guided Analytics Project",
            "difficulty": difficulty,
            "description": "Build an automated sales reporting dashboard using Power Query, Pivot Tables, XLOOKUP, data validation, and interactive slicers.",
            "link": "https://github.com/topics/excel-dashboard",
            "skill_tag": "excel",
            "resource_type": "project_idea"
        }
    elif s in ["r", "r-lang"]:
        return {
            "title": "Statistical Exploratory Data Analysis & Predictive Model in R",
            "provider": "Self-Guided Analytics Project",
            "difficulty": difficulty,
            "description": "Perform regression analysis and interactive data visualization on public healthcare datasets using R, ggplot2, and R Markdown.",
            "link": "https://github.com/topics/r-project",
            "skill_tag": "r",
            "resource_type": "project_idea"
        }
    elif s in ["sql", "mysql", "postgresql"]:
        return {
            "title": "Relational Database Schema Design & Query Optimization Project",
            "provider": "Self-Guided Database Project",
            "difficulty": difficulty,
            "description": "Design a relational database schema, construct complex multi-table inner/outer joins, window functions, and optimize query indexes.",
            "link": "https://github.com/topics/sql-database",
            "skill_tag": "sql",
            "resource_type": "project_idea"
        }
    elif s in ["python", "pandas", "numpy"]:
        return {
            "title": "End-to-End Data Ingestion & Analytics Pipeline",
            "provider": "Self-Guided Python Project",
            "difficulty": difficulty,
            "description": "Build an automated data scraper using Python, clean messy datasets with Pandas, and export visual KPI summaries.",
            "link": "https://github.com/topics/python-analytics",
            "skill_tag": "python",
            "resource_type": "project_idea"
        }
    return {
        "title": f"Applied {skill.capitalize()} Portfolio Project",
        "provider": "Self-Guided Project",
        "difficulty": difficulty,
        "description": f"Build a comprehensive functional system demonstrating core {skill} principles, modular design, and domain validation.",
        "link": "https://github.com/topics/project-ideas",
        "skill_tag": skill,
        "resource_type": "project_idea"
    }

def get_topics_for_skill(skill, week_num):
    s = (skill or "").lower().strip()
    if s in ["excel", "excle", "ms excel", "spreadsheets"]:
        if week_num == 1:
            return ["Excel Formulas & Core Functions (VLOOKUP, XLOOKUP, INDEX/MATCH)", "Data Validation, Formatting, and Logic Operations (IF, AND, OR)"]
        elif week_num == 2:
            return ["Pivot Tables, Pivot Charts, and Dynamic Data Summaries", "Power Query ETL, Data Cleansing, and Executive Dashboard Slicers"]
        elif week_num == 3:
            return ["Microsoft Excel Expert Certification Exam Preparation", "Complex Data Model Validation & Dynamic Array Calculations"]
        else:
            return ["Executive Financial & Sales Analytics Dashboard Execution", "Dynamic KPI Metrics, Interactive Filtering & Formula Optimization"]
    elif s in ["java", "java se", "java developer", "java programming"]:
        if week_num == 1:
            return ["Java SE Syntax, Primitive Types, Control Loops & Encapsulation", "Object-Oriented Programming (Classes, Methods, Arrays)"]
        elif week_num == 2:
            return ["Inheritance, Abstract Classes, Interfaces & Polymorphism", "Java Collections Framework (ArrayList, HashMap, HashSet)"]
        elif week_num == 3:
            return ["Java SE Exception Handling, File I/O & Excel Data Tracking", "Oracle Certified Professional Java SE Developer Exam Practice"]
        else:
            return ["Advanced Java SE: Stream API, Multithreading & Database Connectivity (JDBC)", "Enterprise Java SE Capstone Packaging & Documentation"]
    elif s in ["communication", "presentation", "leadership", "teamwork"]:
        if week_num == 1:
            return ["Verbal & Written Corporate Communication Techniques", "Structuring Technical Proposals and Executive Summaries"]
        else:
            return ["Executive Slide Deck Presentation & Data Storytelling", "Conflict Resolution and Cross-functional Team Leadership"]
    elif s in ["r", "r-lang"]:
        if week_num == 1:
            return ["R Programming Syntax, Vectors, Matrices & Data Frames", "Data Manipulation using dplyr and tidyr packages"]
        else:
            return ["Exploratory Data Analysis and Visualization with ggplot2", "Statistical Modeling, Hypothesis Testing, and R Markdown Reporting"]
    elif s in ["sql", "mysql", "postgresql"]:
        if week_num == 1:
            return ["SQL Query Fundamentals (SELECT, WHERE, ORDER BY, GROUP BY)", "Data Aggregations and Multi-table Joins (INNER, LEFT, RIGHT)"]
        else:
            return ["Subqueries, CTEs, and Window Functions (ROW_NUMBER, RANK)", "Database Schema Design, Indexing, and Performance Tuning"]
    else:
        if week_num == 1:
            return [f"Fundamentals of {skill.capitalize()} and core application rules", f"Foundational workflow setup and practical exercises"]
        else:
            return [f"Advanced {skill.capitalize()} techniques and domain integration", f"Practical portfolio building and real-world application"]

def generate_dual_tier_assessment(skill, week_num):
    s = (skill or "").lower().strip()
    
    soft_rubrics = {
        1: {
            "category": "Soft Skill",
            "skill_name": "Technical Communication & Requirements Analysis",
            "points_allocated": 20,
            "weight_percentage": 20,
            "evaluation_criteria": [
                "Drafting structured problem statements and technical specifications (10 Pts)",
                "Active listening and articulating initial requirements in team reviews (10 Pts)"
            ]
        },
        2: {
            "category": "Soft Skill",
            "skill_name": "Executive Data Storytelling & Presentation Visuals",
            "points_allocated": 20,
            "weight_percentage": 20,
            "evaluation_criteria": [
                "Creating clutter-free slide decks and visual data summaries (10 Pts)",
                "Presenting technical findings effectively to non-technical stakeholders (10 Pts)"
            ]
        },
        3: {
            "category": "Soft Skill",
            "skill_name": "Mock Technical Interview & Verbal Communication",
            "points_allocated": 20,
            "weight_percentage": 20,
            "evaluation_criteria": [
                "Articulating technical trade-offs and architectural decisions verbally (10 Pts)",
                "Answering structured behavioural and scenario-based interview questions (10 Pts)"
            ]
        },
        4: {
            "category": "Soft Skill",
            "skill_name": "Capstone Presentation & Project Documentation Portfolio",
            "points_allocated": 20,
            "weight_percentage": 20,
            "evaluation_criteria": [
                "Writing comprehensive technical README and project documentation (10 Pts)",
                "Delivering a live video walkthrough and fielding peer Q&A feedback (10 Pts)"
            ]
        }
    }
    
    soft_assessment = soft_rubrics.get(week_num, soft_rubrics[1])
    
    if s in ["excel", "excle", "ms excel", "spreadsheets"]:
        tech_rubrics = {
            1: ["Excel formula syntax: VLOOKUP, XLOOKUP, INDEX/MATCH (40 Pts)", "Logical operations: IF, AND, OR, and data validation rules (40 Pts)"],
            2: ["Pivot Tables, Pivot Charts, and dynamic slicers (40 Pts)", "Power Query ETL workflows and raw data cleansing (40 Pts)"],
            3: ["Timed Excel Expert mock assessment & error debugging (40 Pts)", "Complex data model validation & dynamic array calculations (40 Pts)"],
            4: ["Automated Executive Financial & Sales Analytics Dashboard execution (40 Pts)", "Dynamic KPI metrics, interactive filtering, and formula optimization (40 Pts)"]
        }
        tech_skill_name = "Microsoft Excel Core & Advanced Data Analytics"
    elif s in ["r", "r-lang"]:
        tech_rubrics = {
            1: ["R syntax, vectors, matrices, and data frame manipulation (40 Pts)", "Data wrangling using dplyr and tidyr packages (40 Pts)"],
            2: ["Exploratory Data Analysis and statistical visualizations with ggplot2 (40 Pts)", "Regression modeling, hypothesis testing, and R Markdown reporting (40 Pts)"],
            3: ["Timed R Data Analyst assessment & script debugging (40 Pts)", "Statistical model evaluation and metric verification (40 Pts)"],
            4: ["Applied Statistical EDA & Predictive Model project implementation (40 Pts)", "R Markdown report generation and reproducible code pipeline (40 Pts)"]
        }
        tech_skill_name = "R Statistical Programming & Predictive Modeling"
    elif s in ["sql", "mysql", "postgresql"]:
        tech_rubrics = {
            1: ["SQL DDL/DML query syntax, SELECT, WHERE, ORDER BY (40 Pts)", "Multi-table INNER, LEFT, RIGHT JOIN aggregations (40 Pts)"],
            2: ["Subqueries, CTEs, and Window Functions (ROW_NUMBER, RANK) (40 Pts)", "Database schema design, indexing, and query plan optimization (40 Pts)"],
            3: ["Timed SQL Associate evaluation & query debugging (40 Pts)", "Complex multi-table aggregation benchmark (40 Pts)"],
            4: ["Relational Database System Design & Query Optimization Capstone (40 Pts)", "Schema validation, index efficiency tuning, and benchmark report (40 Pts)"]
        }
        tech_skill_name = "SQL Relational Database Engineering"
    else:
        tech_rubrics = {
            1: [f"Core {skill.capitalize()} syntax, data structures, and foundational exercises (40 Pts)", f"Basic implementation and unit verification (40 Pts)"],
            2: [f"Intermediate & advanced {skill.capitalize()} design patterns (40 Pts)", f"Integration testing and workflow optimization (40 Pts)"],
            3: [f"Timed {skill.capitalize()} technical evaluation & error handling (40 Pts)", f"Algorithm efficiency and benchmark validation (40 Pts)"],
            4: [f"Applied {skill.capitalize()} Capstone Project System implementation (40 Pts)", f"Production execution, deployment, and code quality verification (40 Pts)"]
        }
        tech_skill_name = f"{skill.capitalize()} Core Technical Mastery"
        
    core_tech_assessment = {
        "category": "Core Technical Skill",
        "skill_name": tech_skill_name,
        "points_allocated": 80,
        "weight_percentage": 80,
        "evaluation_criteria": tech_rubrics.get(week_num, tech_rubrics[1])
    }
    
    return core_tech_assessment, soft_assessment

def assemble_4_week_plan(missing_skills_list, student_cgpa=7.5, resources_path="data/learning_resources.json"):
    """
    Assembles a structured 4-week recommendation plan for a student based on missing skills.
    """
    skills = [s for s in missing_skills_list if s.get('importance_weight', 0) > 0]
    skills.sort(key=lambda x: x.get('importance_weight', 0), reverse=True)
    
    if not skills:
        skills = [
            {"required_skill": "excel", "importance_weight": 5},
            {"required_skill": "sql", "importance_weight": 4},
            {"required_skill": "python", "importance_weight": 3}
        ]
        
    if student_cgpa >= 8.5:
        project_difficulty = "hard"
    elif student_cgpa >= 7.0:
        project_difficulty = "intermediate"
    else:
        project_difficulty = "easy"
        
    soft_tags = [
        "communication", "presentation", "leadership", "teamwork", "soft skills", "soft skill",
        "agile", "collaboration", "management", "problem solving", "problem-solving", "problem_solving",
        "critical thinking", "analytical skills", "troubleshooting", "time management",
        "interpersonal skills", "work ethic", "creativity"
    ]
    tech_skills = [s for s in skills if s['required_skill'].lower().strip() not in soft_tags]
    
    # Always prioritize core technical skills (Excel, SQL, Python, R, Java, React, Docker, etc.) over soft skills
    if not tech_skills:
        tech_skills = [
            {"required_skill": "excel", "importance_weight": 5},
            {"required_skill": "sql", "importance_weight": 4},
            {"required_skill": "python", "importance_weight": 3}
        ]
        
    primary_skill = tech_skills[0]['required_skill'].lower().strip()
    secondary_skill = tech_skills[1]['required_skill'].lower().strip() if len(tech_skills) > 1 else primary_skill
        
    primary_resources = retrieve_resources_for_skill(primary_skill, top_k=5, resources_path=resources_path)
    secondary_resources = retrieve_resources_for_skill(secondary_skill, top_k=5, resources_path=resources_path)
    
    # Week 1: Primary Skill Fundamentals
    w1_resources = [r for r in primary_resources if r['resource_type'] in ['course', 'youtube']][:2]
    if not w1_resources:
        w1_resources = primary_resources[:2]
        
    # Week 2: Secondary Skill / Advanced Primary
    w2_resources = [r for r in secondary_resources if r['resource_type'] in ['course', 'youtube']][:2]
    if not w2_resources or secondary_skill == primary_skill:
        # Fallback to remaining primary resources if no distinct secondary skill
        w2_resources = [r for r in primary_resources if r not in w1_resources][:2]
        if not w2_resources:
            w2_resources = primary_resources[:2]
            
    # Week 3: Certifications (strictly matched to primary_skill)
    w3_resources = [
        r for r in primary_resources 
        if r.get('resource_type') == 'certification' and r.get('skill_tag', '').lower().strip() == primary_skill
    ]
    seen_certs = set()
    dedup_certs = []
    for c in w3_resources:
        if c['title'] not in seen_certs:
            seen_certs.add(c['title'])
            dedup_certs.append(c)
    w3_resources = dedup_certs[:2]
    
    if not w3_resources:
        if "communication" in primary_skill or "presentation" in primary_skill or "soft" in primary_skill:
            w3_resources = [
                {
                    "title": "Professional Business Communication & Executive Presence Certificate",
                    "provider": "Coursera (Wharton School)",
                    "difficulty": "intermediate",
                    "description": "Professional credential certifying mastery in executive presentations, business writing, and corporate communication.",
                    "link": "https://www.coursera.org/learn/wharton-communication-skills",
                    "resource_type": "certification",
                    "skill_tag": "communication"
                }
            ]
        elif "excel" in primary_skill or "excle" in primary_skill or "spreadsheet" in primary_skill:
            w3_resources = [
                {
                    "title": "Microsoft Office Specialist: Excel Expert (MO-201)",
                    "provider": "Microsoft",
                    "difficulty": "intermediate",
                    "description": "Official Microsoft certification validating expertise in advanced formulas, custom data formats, and Power Pivot models.",
                    "link": "https://learn.microsoft.com/en-us/credentials/certifications/mos-excel-expert-2019",
                    "resource_type": "certification",
                    "skill_tag": "excel"
                },
                {
                    "title": "Microsoft Certified: Power BI Data Analyst Associate (PL-300)",
                    "provider": "Microsoft",
                    "difficulty": "hard",
                    "description": "Demonstrate expertise in converting raw Excel datasets into actionable Business Intelligence dashboards.",
                    "link": "https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/",
                    "resource_type": "certification",
                    "skill_tag": "excel"
                }
            ]
        else:
            w3_resources = [
                {
                    "title": "Google Data Analytics Professional Certificate",
                    "provider": "Coursera (Google)",
                    "difficulty": "intermediate",
                    "description": "Gain in-demand skills in data cleaning, analysis, visualization, and spreadsheets.",
                    "link": "https://www.coursera.org/professional-certificates/google-data-analytics",
                    "resource_type": "certification",
                    "skill_tag": primary_skill
                }
            ]

    # Week 4: Applied Capstone Project
    w4_projects = [r for r in primary_resources if r.get('resource_type') == 'project_idea']
    if w4_projects:
        suggested_project = w4_projects[0]
    else:
        suggested_project = generate_domain_project(primary_skill, project_difficulty)
        
    weeks_plan = []
    
    # Week 1
    w1_topics = get_topics_for_skill(primary_skill, 1)
    w1_tech_eval, w1_soft_eval = generate_dual_tier_assessment(primary_skill, 1)
    weeks_plan.append({
        "week": 1,
        "topic": f"Fundamentals of {primary_skill.upper()}",
        "focus_skill": primary_skill,
        "learning_objectives": w1_topics,
        "core_technical_assessment": w1_tech_eval,
        "soft_skill_assessment": w1_soft_eval,
        "total_weekly_points": 100,
        "resources": w1_resources,
        "suggested_project": None,
        "summary_text": f"Week 1: Focus on {primary_skill.capitalize()} core fundamentals and essential operations."
    })
    
    # Week 2
    w2_skill = secondary_skill if secondary_skill != primary_skill else primary_skill
    w2_topics = get_topics_for_skill(w2_skill, 2)
    w2_tech_eval, w2_soft_eval = generate_dual_tier_assessment(w2_skill, 2)
    weeks_plan.append({
        "week": 2,
        "topic": f"Intermediate & Advanced {w2_skill.upper()}",
        "focus_skill": w2_skill,
        "learning_objectives": w2_topics,
        "core_technical_assessment": w2_tech_eval,
        "soft_skill_assessment": w2_soft_eval,
        "total_weekly_points": 100,
        "resources": w2_resources,
        "suggested_project": None,
        "summary_text": f"Week 2: Focus on {w2_skill.capitalize()} advanced analytics and practical workflows."
    })
    
    # Week 3
    w3_topics = get_topics_for_skill(primary_skill, 3)
    w3_tech_eval, w3_soft_eval = generate_dual_tier_assessment(primary_skill, 3)
    weeks_plan.append({
        "week": 3,
        "topic": f"Professional Certification & Evaluation ({primary_skill.upper()})",
        "focus_skill": primary_skill,
        "learning_objectives": w3_topics,
        "core_technical_assessment": w3_tech_eval,
        "soft_skill_assessment": w3_soft_eval,
        "total_weekly_points": 100,
        "resources": w3_resources,
        "suggested_project": None,
        "summary_text": f"Week 3: Target professional certification in {primary_skill.capitalize()} and complete mock assessments."
    })
    
    # Week 4
    w4_topics = get_topics_for_skill(primary_skill, 4)
    w4_tech_eval, w4_soft_eval = generate_dual_tier_assessment(primary_skill, 4)
    weeks_plan.append({
        "week": 4,
        "topic": f"Capstone Project: {suggested_project['title']}",
        "focus_skill": primary_skill,
        "learning_objectives": w4_topics,
        "core_technical_assessment": w4_tech_eval,
        "soft_skill_assessment": w4_soft_eval,
        "total_weekly_points": 100,
        "resources": [suggested_project],
        "suggested_project": suggested_project,
        "summary_text": f"Week 4: Execute hands-on Capstone Project: '{suggested_project['title']}'."
    })
    
    recommendation_output = {
        "student_cgpa": student_cgpa,
        "project_difficulty_level": project_difficulty,
        "weeks": weeks_plan,
        "text_summary": "\n\n".join([w["summary_text"] for w in weeks_plan])
    }
    
    return recommendation_output

if __name__ == "__main__":
    res_path = "data/learning_resources.json"
    print("\nAssembling learning plan for missing skills: ['excel']...")
    missing_skills = [{"required_skill": "excel", "importance_weight": 5}]
    plan = assemble_4_week_plan(missing_skills, student_cgpa=8.0, resources_path=res_path)
    for w in plan["weeks"]:
        print(f"\nWeek {w['week']} - Focus: {w['focus_skill'].upper()} ({w['topic']})")
        for r in w["resources"]:
            print(f"  [{r['resource_type'].upper()}] {r['title']} ({r['provider']})")
