import os
import logging
from typing import Dict, Any
from groq import Groq

# Configure logger
logger = logging.getLogger("groq_enhance")
logging.basicConfig(level=logging.INFO)

def enhance_plan_with_llm(plan_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches the personal learning plan and project descriptions using the Groq API.
    Fails gracefully to the rule-based templates if the API key is missing,
    rate limits are hit, or if the request times out (5-second threshold).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.info("GROQ_API_KEY not found in environment. Using standard template plan.")
        return plan_dict

    try:
        # Initialize Groq client with a strict timeout of 5 seconds
        client = Groq(api_key=api_key, timeout=5.0)

        # Prepare a structured prompt summarizing the current plan details
        weekly_focuses = [f"Week {w['week']}: {w['focus_skill']} (Topics: {', '.join(w['topics'])})" for w in plan_dict.get("plan", [])]
        capstone = plan_dict.get("capstone_project", {})
        
        prompt = f"""
You are an expert AI Career Coach. I will provide you with a structured student learning plan and a capstone project suggestion. 
Enhance the capstone project description and weekly summaries to make them highly actionable, professional, and personalized.

Target Capstone Project:
Title: {capstone.get('title')}
Technologies: {', '.join(capstone.get('technologies', []))}
Current Description: {capstone.get('description')}

Current Weekly Focus Areas:
{chr(10).join(weekly_focuses)}

Provide your output in valid JSON matching this format:
{{
  "enhanced_capstone_description": "Enriched project description here...",
  "weekly_coach_tips": [
    "Tip for week 1...",
    "Tip for week 2...",
    "Tip for week 3...",
    "Tip for week 4..."
  ]
}}

Ensure you only return valid JSON. Do not include markdown code block formatting or wrapping.
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=600,
        )

        response_text = chat_completion.choices[0].message.content
        import json
        enhanced_data = json.loads(response_text)

        # Build enhanced plan response by merging details
        enhanced_plan = json.loads(json.dumps(plan_dict)) # Deep copy
        
        # Inject enhanced project description
        if "enhanced_capstone_description" in enhanced_data:
            enhanced_plan["capstone_project"]["description"] = enhanced_data["enhanced_capstone_description"]
        
        # Inject weekly tips into each week
        tips = enhanced_data.get("weekly_coach_tips", [])
        for i, week in enumerate(enhanced_plan.get("plan", [])):
            if i < len(tips):
                week["coach_tip"] = tips[i]
            else:
                week["coach_tip"] = "Focus on mastering the core concepts and building hands-on exercises."

        logger.info("Successfully enhanced learning plan via Groq API.")
        return enhanced_plan

    except Exception as e:
        logger.error(f"Groq API enhancement failed or timed out. Falling back to template plan. Error: {str(e)}")
        # Safe fallback: return the original dictionary unmodified
        fallback_plan = json.loads(json.dumps(plan_dict)) if 'json' in locals() else plan_dict
        # Auto-inject default coach tips in case of fallback
        for week in fallback_plan.get("plan", []):
            if "coach_tip" not in week:
                week["coach_tip"] = "Complete the recommended courses and projects to strengthen your core proficiency."
        return fallback_plan
