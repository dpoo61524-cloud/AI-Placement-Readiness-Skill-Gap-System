"""
generate_project_graph.py
Generates a visual architecture graph for the AI Placement Readiness project
using matplotlib. Saved to PROJECT_OVERVIEW/project_graph.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(22, 16))
ax.set_xlim(0, 22)
ax.set_ylim(0, 16)
ax.axis('off')
fig.patch.set_facecolor('#0d1117')

def box(ax, x, y, w, h, label, sublabel="", color="#1f6feb", text_color="white", done=True, fontsize=9):
    edge_color = "#3fb950" if done else "#f85149"
    status_char = "✓" if done else "○"
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                           facecolor=color, edgecolor=edge_color, linewidth=2.5, zorder=3)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2 + (0.12 if sublabel else 0), f"{status_char} {label}",
            ha='center', va='center', fontsize=fontsize, fontweight='bold',
            color=text_color, zorder=4, wrap=True)
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.22, sublabel,
                ha='center', va='center', fontsize=7.5,
                color="#8b949e", zorder=4)

def arrow(ax, x1, y1, x2, y2, color="#58a6ff"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=2.0),
                zorder=2)

def section_label(ax, x, y, text, color="#58a6ff"):
    ax.text(x, y, text, ha='left', va='center', fontsize=11, fontweight='bold',
            color=color, zorder=5)

# ─────────────── TITLE ───────────────
ax.text(11, 15.4, "AI Placement Readiness & Skill Gap System",
        ha='center', va='center', fontsize=17, fontweight='bold', color='white')
ax.text(11, 14.95, "Full-Stack Architecture Graph  ·  All Parts Completed ✓",
        ha='center', va='center', fontsize=10, color='#8b949e')

# ─────────────── LEGEND ───────────────
done_patch = mpatches.Patch(color='#3fb950', label='Completed ✓')
todo_patch = mpatches.Patch(color='#f85149', label='Not Done ○')
ax.legend(handles=[done_patch, todo_patch], loc='upper right',
          facecolor='#161b22', edgecolor='#30363d', labelcolor='white',
          fontsize=9, bbox_to_anchor=(0.99, 0.99))

# ══════════════════════════════════════════════
# ROW 1 — INPUTS
# ══════════════════════════════════════════════
section_label(ax, 0.4, 14.3, "INPUTS", "#f0883e")
box(ax, 1.5,  13.5, 3.2, 0.75, "Resume PDF", "Student uploads PDF", "#0e4429", done=True)
box(ax, 5.5,  13.5, 3.2, 0.75, "Job Description", "Paste JD text", "#0e4429", done=True)

# ══════════════════════════════════════════════
# ROW 2 — PART 1: DATA & ML
# ══════════════════════════════════════════════
section_label(ax, 0.4, 12.8, "PART 1 — ML PIPELINE", "#58a6ff")

# Left column: Data Generation
box(ax, 0.3, 11.8, 3.5, 0.85, "data_prep.py", "2000 synthetic students\ndata/placement_data.csv", "#1c2d41", done=True, fontsize=8.5)
box(ax, 0.3, 10.7, 3.5, 0.85, "train_model.py", "RF vs XGBoost → F1=0.9246\nmodels/placement_model.pkl", "#1c2d41", done=True, fontsize=8.5)

# Middle column: Parsing
box(ax, 4.5, 11.8, 3.5, 0.85, "resume_parser.py", "pdfplumber + regex\nSkill extraction, CGPA, backlogs", "#1c2d41", done=True, fontsize=8.5)
box(ax, 4.5, 10.7, 3.5, 0.85, "explain.py", "SHAP TreeExplainer\nPer-feature contributions JSON", "#1c2d41", done=True, fontsize=8.5)

# Right column: Skill Gap
box(ax, 8.6, 11.8, 3.8, 0.85, "skill_gap.py", "MiniLM-L6-v2 embeddings\nFAISS cosine similarity → gap list", "#1c2d41", done=True, fontsize=8.5)
box(ax, 8.6, 10.7, 3.8, 0.85, "skill_importance.json", "15 reference JDs\nFrequency-based 1-5 weights", "#1c2d41", done=True, fontsize=8.5)

# Outputs row
box(ax, 1.0,  9.65, 2.0, 0.75, "placement_data.csv", "", "#0d2b12", done=True, fontsize=8)
box(ax, 3.3,  9.65, 2.0, 0.75, "preprocessor.joblib", "", "#0d2b12", done=True, fontsize=8)
box(ax, 5.6,  9.65, 2.0, 0.75, "placement_model.pkl", "", "#0d2b12", done=True, fontsize=8)
box(ax, 7.9,  9.65, 2.0, 0.75, "shap_summary.png", "", "#0d2b12", done=True, fontsize=8)
box(ax, 10.1, 9.65, 2.1, 0.75, "pipeline_output.json", "", "#0d2b12", done=True, fontsize=8)

# Arrows Part 1
arrow(ax, 3.1, 13.87, 0.3+3.5/2, 12.65)
arrow(ax, 5.1, 13.87, 4.5+3.5/2, 12.65)
arrow(ax, 2.05, 11.8, 2.05, 11.55)
arrow(ax, 6.25, 11.8, 6.25, 11.55)
arrow(ax, 10.5, 11.8, 10.5, 11.55)

# ══════════════════════════════════════════════
# ROW 3 — PART 2: RAG + BACKEND
# ══════════════════════════════════════════════
section_label(ax, 0.4, 9.1, "PART 2 — RAG ENGINE + FASTAPI BACKEND", "#58a6ff")

box(ax, 0.3,  7.9, 3.5, 0.85, "recommendation.py", "FAISS IndexFlatL2\n50 resources → 4-week plan", "#1c2d41", done=True, fontsize=8.5)
box(ax, 4.2,  7.9, 3.5, 0.85, "learning_resources.json", "50 curated resources\nCourses, YouTube, Certs, Projects", "#1c2d41", done=True, fontsize=8.5)
box(ax, 8.0,  7.9, 3.5, 0.85, "backend/main.py", "FastAPI + CORS\nStartup FAISS preloading", "#1c2d41", done=True, fontsize=8.5)
box(ax, 11.8, 7.9, 3.5, 0.85, "backend/db/", "SQLAlchemy + SQLite\ncache.db  ·  SubmissionCache", "#1c2d41", done=True, fontsize=8.5)

# Endpoints row
endpoints = [
    ("POST /parse-resume", 0.3),
    ("POST /predict", 2.6),
    ("POST /skill-gap", 4.9),
    ("POST /recommendations", 7.2),
    ("POST /full-analysis", 9.8),
    ("GET /health", 12.4),
    ("GET /history", 14.7),
]
for label, xpos in endpoints:
    box(ax, xpos, 6.7, 2.1, 0.75, label, "", "#1c2d41", done=True, fontsize=7.5)

# Caching badge
box(ax, 15.5, 7.9, 2.8, 0.85, "SHA256 Cache", "Cache hit ~10ms\nvs ~500ms cold run", "#261e06", done=True, fontsize=8.5)

# Arrow Part 2
for label, xpos in endpoints:
    arrow(ax, 9.75, 7.9, float(xpos)+1.05, 7.45)

# ══════════════════════════════════════════════
# ROW 4 — PART 3: FRONTEND (NOT DONE)
# ══════════════════════════════════════════════
section_label(ax, 0.4, 6.25, "PART 3 — REACT FRONTEND DASHBOARD  ✓ COMPLETED", "#3fb950")

frontend_blocks = [
    ("Upload Page", "Drag & drop PDF\n+ JD text area"),
    ("Dashboard Page", "Gauge, SHAP bar\nRadar, Gap bar"),
    ("Recommendations", "4-week accordion\nResource links"),
    ("History Page", "Past submissions\nfrom SQLite cache"),
    ("API Client", "Axios calls to\nFastAPI endpoints"),
]
for i, (title, sub) in enumerate(frontend_blocks):
    box(ax, 0.3 + i*4.3, 5.1, 3.9, 0.9, title, sub, "#1c2d41", done=True, fontsize=8.5)

# ══════════════════════════════════════════════
# ROW 5 — PART 4: DEPLOYMENT (NOT DONE)
# ══════════════════════════════════════════════
section_label(ax, 0.4, 4.6, "PART 4 — DEPLOYMENT + GROQ LLM LAYER  ✓ COMPLETED", "#3fb950")

deploy_blocks = [
    ("Render/Railway", "Backend deploy\nDockerfile / render.yaml"),
    ("Vercel/Netlify", "Frontend deploy\nVite build config"),
    ("Groq API", "Natural language\nplan enhancement"),
    ("Template Fallback", "Part 2 template\nif Groq fails"),
    ("Rate Limiting", "Protect free tier\nin-memory limiter"),
    (".env Config", "GROQ_API_KEY\nDATABASE_URL\nCORS_ORIGINS"),
]
for i, (title, sub) in enumerate(deploy_blocks):
    box(ax, 0.3 + i*3.6, 3.4, 3.3, 0.9, title, sub, "#1c2d41", done=True, fontsize=8.5)

# ══════════════════════════════════════════════
# BOTTOM: KEY FILES MAP
# ══════════════════════════════════════════════
ax.text(11, 2.7, "Key Artifact Files", ha='center', fontsize=10, fontweight='bold', color='#58a6ff')
files = [
    "data/placement_data.csv", "data/skill_importance.json", "data/learning_resources.json",
    "models/placement_model.pkl", "models/preprocessor.joblib", "models/shap_summary.png",
    "src/data_prep.py", "src/train_model.py", "src/explain.py",
    "src/resume_parser.py", "src/skill_gap.py", "src/recommendation.py",
    "backend/main.py", "backend/schemas.py", "backend/routers/analysis.py",
    "backend/db/session.py", "backend/db/models.py", "tests/test_pipeline.py",
    "tests/test_api.py", "requirements.txt",
]
per_row = 5
for i, f in enumerate(files):
    row = i // per_row
    col = i % per_row
    ax.text(1.2 + col*4.1, 2.2 - row*0.4, f"• {f}", ha='left', fontsize=7.8,
            color='#3fb950' if row < 4 else '#8b949e')

plt.tight_layout()
plt.savefig("PROJECT_OVERVIEW/project_graph.png", dpi=160, bbox_inches='tight',
            facecolor='#0d1117')
plt.close()
print("Graph saved -> PROJECT_OVERVIEW/project_graph.png")
