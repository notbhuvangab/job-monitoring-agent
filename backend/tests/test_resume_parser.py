"""Tests for resume parser service."""
import pytest
from services.resume_parser import ResumeParser


def test_parse_text_with_skills():
    """Test parsing resume text with skills."""
    resume_text = """
    John Doe
    Software Engineer
    
    Skills: Python, JavaScript, React, Django, PostgreSQL, Docker
    
    Experience:
    Senior Developer at Tech Corp (2020-2023)
    - Built scalable web applications
    - Led a team of 5 engineers
    
    Education:
    Bachelor of Science in Computer Science
    University of Tech, 2020
    """
    
    parsed = ResumeParser.parse_text(resume_text)
    
    assert "skills" in parsed
    assert "experiences" in parsed
    assert "education" in parsed
    assert "embedding" in parsed
    
    # Check that common skills are detected
    skills = parsed["skills"]
    assert "python" in skills
    assert "javascript" in skills or "react" in skills


def test_extract_skills():
    """Test skill extraction."""
    text = "Experience with python, react, docker, and postgresql"
    skills = ResumeParser._extract_skills(text)
    
    assert "python" in skills
    assert "react" in skills
    assert "docker" in skills
    assert "postgresql" in skills


def test_parse_empty_resume():
    """Test parsing empty resume."""
    resume_text = ""
    
    with pytest.raises(Exception):
        ResumeParser.parse_text(resume_text)

