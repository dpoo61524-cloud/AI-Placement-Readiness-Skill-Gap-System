from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# 1. Student Features Schema
class StudentFeatures(BaseModel):
    CGPA: float = Field(..., ge=0.0, le=10.0, description="Cumulative Grade Point Average (0.0 to 10.0)")
    backlogs: int = Field(..., ge=0, le=20, description="Number of active/history backlogs")
    internships: int = Field(..., ge=0, le=10, description="Number of completed internships")
    projects: int = Field(..., ge=0, le=20, description="Number of academic/personal projects")
    certifications: int = Field(..., ge=0, le=20, description="Number of completed certifications")
    coding_score: float = Field(..., ge=0.0, le=100.0, description="Coding test score (0.0 to 100.0)")
    communication_score: float = Field(..., ge=0.0, le=100.0, description="Communication/Interview score (0.0 to 100.0)")
    specialization: str = Field(..., description="Student branch specialization")

# 2. Predict Endpoint schemas
class FeatureContribution(BaseModel):
    value: Any
    contribution: float

class PredictResponse(BaseModel):
    readiness_probability: float = Field(..., description="Placement readiness probability [0, 1]")
    base_probability: float = Field(..., description="Average base probability of placement [0, 1]")
    contributions: Dict[str, FeatureContribution] = Field(..., description="SHAP feature contribution values")

# 3. Skill Gap Endpoint schemas
class SkillGapItem(BaseModel):
    required_skill: str
    matched_student_skill: Optional[str] = None
    similarity_score: float
    importance_weight: int

class SkillGapRequest(BaseModel):
    resume_skills: List[str]
    job_description: str

class SkillGapResponse(BaseModel):
    matched: List[SkillGapItem]
    partially_matched: List[SkillGapItem]
    missing: List[SkillGapItem]

# 4. Recommendation schemas
class LearningResource(BaseModel):
    skill_tag: Optional[str] = None
    resource_type: Optional[str] = None
    title: str
    provider: str
    difficulty: str
    description: str
    link: str

class DualTierAssessmentItem(BaseModel):
    category: str = Field(..., description="'Core Technical Skill' or 'Soft Skill'")
    skill_name: str
    points_allocated: int = Field(..., description="Points allocated out of 100 weekly total (e.g. 80 for Core, 20 for Soft)")
    weight_percentage: int = Field(..., description="Percentage weight (e.g. 80% or 20%)")
    evaluation_criteria: List[str]

class WeekPlan(BaseModel):
    week: int
    topic: str
    focus_skill: str
    learning_objectives: List[str]
    core_technical_assessment: DualTierAssessmentItem
    soft_skill_assessment: DualTierAssessmentItem
    total_weekly_points: int = 100
    resources: List[LearningResource]
    suggested_project: Optional[LearningResource] = None
    summary_text: str
    coach_tip: Optional[str] = None


class RecommendationsRequest(BaseModel):
    missing_skills: List[Dict[str, Any]] = Field(..., description="List of missing skills with weights")
    student_cgpa: float = Field(7.5, ge=0.0, le=10.0)

class RecommendationsResponse(BaseModel):
    student_cgpa: float
    project_difficulty_level: str
    weeks: List[WeekPlan]
    text_summary: str

# 5. Full Analysis schemas
class StudentProfile(BaseModel):
    features: StudentFeatures
    resume_skills: List[str]

class JobProfile(BaseModel):
    required_skills: List[str]

class ShapExplanation(BaseModel):
    base_probability: float
    contributions: Dict[str, FeatureContribution]

class FullAnalysisReadiness(BaseModel):
    placement_readiness_score: float
    shap_explanation: ShapExplanation

class FullAnalysisResponse(BaseModel):
    student_profile: StudentProfile
    job_profile: JobProfile
    readiness_analysis: FullAnalysisReadiness
    skill_gap_analysis: SkillGapResponse
    recommendation_plan: RecommendationsResponse

# 6. History Item schema
class HistoryItem(BaseModel):
    input_hash: str
    timestamp: datetime
    resume_filename: Optional[str]
    result: FullAnalysisResponse
