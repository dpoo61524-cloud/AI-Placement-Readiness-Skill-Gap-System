import os
from fpdf import FPDF

def create_resume_pdf(filename, name, email, degree, cgpa, backlogs, skills_lang, skills_tools, soft_skills, projects_text, experience_text, cert_text):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=name, ln=1, align="C")
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt=f"Email: {email} | Phone: +91 9876543210", ln=1, align="C")
    pdf.cell(200, 5, txt=f"Education: {degree}", ln=1, align="C")
    pdf.cell(200, 5, txt=f"CGPA: {cgpa} / 10 | Backlogs: {backlogs}", ln=1, align="C")
    pdf.ln(5)
    
    # Skills
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Technical & Soft Skills", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt=f"Languages: {skills_lang}", ln=1)
    pdf.cell(200, 5, txt=f"Frameworks & Tools: {skills_tools}", ln=1)
    pdf.cell(200, 5, txt=f"Soft Skills: {soft_skills}", ln=1)
    pdf.ln(5)
    
    # Projects
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Projects", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, txt=projects_text)
    pdf.ln(5)
    
    # Experience
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Work Experience & Internships", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, txt=experience_text)
    pdf.ln(5)
    
    # Certifications
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 8, txt="Certifications", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt=cert_text, ln=1)
    
    pdf.output(filename)
    print(f"Generated sample resume PDF: {filename}")

if __name__ == "__main__":
    # 1. High Match Profile
    create_resume_pdf(
        "data/sample_resume_high_match.pdf",
        "Siddharth Sharma",
        "siddharth.sharma@email.com",
        "Bachelor of Technology in Computer Science & Engineering",
        "8.85", "0",
        "Python, Java, SQL, Javascript, C++",
        "React, Spring Boot, Git, Docker, OpenCV",
        "Communication, Presentation, Teamwork, Agile",
        "1. AI Attendance System: Built using Python and OpenCV for facial recognition.\n2. Portfolio Website: Developed an interactive responsive site using React and Tailwind.",
        "Software Engineer Intern at Technosoft Systems (2 months)\nWorked on backend API modules in Python and SQL databases.",
        "- AWS Certified Solutions Architect - Associate"
    )
    
    # 2. Medium Match Profile
    create_resume_pdf(
        "data/sample_resume_medium_match.pdf",
        "Ananya Verma",
        "ananya.verma@email.com",
        "Bachelor of Technology in Information Technology",
        "7.20", "0",
        "Java, HTML, CSS, SQL, JavaScript",
        "Git, Bootstrap, Node.js",
        "Teamwork, Communication, Problem Solving",
        "1. E-Commerce Storefront: Responsive shopping cart application using HTML/CSS/JavaScript.",
        "Web Developer Intern at Local Tech Solutions (1 month)",
        "- Oracle Certified Associate Java Programmer"
    )
    
    # 3. Gap Match Profile
    create_resume_pdf(
        "data/sample_resume_gap_match.pdf",
        "Rohan Gupta",
        "rohan.gupta@email.com",
        "Bachelor of Technology in Electronics & Communication",
        "6.40", "1",
        "C++, C, Basic Python",
        "Git",
        "Adaptability, Teamwork",
        "1. Embedded Temperature Sensor: Microcontroller project using C++.",
        "No formal internships completed.",
        "- Basic Python Programming Certificate"
    )
