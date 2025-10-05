"""Job scoring service using LLM - completely simplified."""
from typing import Dict, Any, Tuple
from openai import OpenAI
from config import get_settings
from utils import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


class JobScorer:
    """Score jobs against resume using LLM - no manual extraction needed!"""
    
    @staticmethod
    def score_job(
        job_data: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Score job against resume using LLM.
        
        The LLM analyzes the full resume text and job description,
        extracts skills automatically, and provides intelligent matching.
        """
        try:
            if not client:
                logger.warning("No OpenAI API key - using basic fallback")
                return JobScorer._simple_fallback(job_data, resume_data)
            
            # Get resume content (just the text!)
            resume_content = resume_data.get("content", "")
            if not resume_content or len(resume_content) < 50:
                logger.error("Resume content missing or too short")
                return 0.0, {"error": "No resume content", "matched_keywords": []}
            
            # Build job summary
            job_summary = f"""Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}
Location: {job_data.get('location', 'N/A')}
Type: {job_data.get('type', 'N/A')}
Description: {job_data.get('description', 'N/A')[:1500]}"""
            
            # LLM prompt - let it extract everything
            prompt = f"""You are an expert resume-job matching AI. Score how well this candidate matches the job.

CANDIDATE'S RESUME:
{resume_content[:3000]}

JOB POSTING:
{job_summary}

Analyze the match by:
1. Extracting skills from the resume
2. Identifying required skills in the job description
3. Comparing experience level and responsibilities
4. Evaluating education fit
5. Considering location/remote preferences

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "score": <integer 0-100>,
  "reasoning": "<concise 1-2 sentence explanation>",
  "matched_skills": [<array of strings: skills that match>]
}}

Scoring guide:
- 90-100: Perfect match (all requirements + ideal candidate)
- 75-89: Strong match (meets most requirements well)
- 60-74: Good match (meets key requirements)
- 40-59: Moderate match (some relevant experience)
- 0-39: Weak match (few relevant qualifications)"""
            
            # Call LLM
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=400
            )
            
            # Parse JSON response
            import json
            response_text = response.choices[0].message.content.strip()
            
            # Clean markdown if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            score = float(result.get("score", 0))
            score = max(0, min(100, score))  # Clamp 0-100
            
            details = {
                "score": round(score, 2),
                "llm_reasoning": str(result.get("reasoning", ""))[:500],
                "matched_keywords": [str(s) for s in result.get("matched_skills", [])[:20]],
                "total_keywords_matched": len(result.get("matched_skills", []))
            }
            
            logger.info(f"LLM scored '{job_data.get('title')}': {score}/100")
            return score, details
            
        except Exception as e:
            logger.error(f"LLM scoring error: {e}")
            return JobScorer._simple_fallback(job_data, resume_data)
    
   