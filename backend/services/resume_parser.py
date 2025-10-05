"""Resume parsing service - simplified for LLM."""
import re
from typing import Dict, Any
from PyPDF2 import PdfReader
from io import BytesIO
from utils import get_logger

logger = get_logger(__name__)


class ResumeParser:
    """Parse resume - simplified to let LLM do the heavy lifting."""
    
    @staticmethod
    def parse_pdf(pdf_file: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PdfReader(BytesIO(pdf_file))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    @staticmethod
    def parse_text(text: str) -> Dict[str, Any]:
        """
        Parse resume text - just store it, let LLM analyze it.
        No complex extraction needed - LLM does it all!
        """
        try:
            if not text or len(text.strip()) < 50:
                raise ValueError("Resume text is too short or empty")
            
            # Just normalize whitespace
            text = re.sub(r"\r\n?", "\n", text)
            text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 consecutive newlines
            
            logger.info(f"Parsed resume: {len(text)} characters")
            
            return {
                "content": text.strip(),
                "skills": [],  
                "experiences": [], 
                "education": []  
            }
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise
