"""Embedding generation service."""
import openai
from typing import List
from sentence_transformers import SentenceTransformer
from config import get_settings
from utils import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Cache for embedding model
_embedding_model = None


def get_embedding_model():
    """Get or create embedding model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading local embedding model: {settings.local_embedding_model}")
        _embedding_model = SentenceTransformer(settings.local_embedding_model)
    return _embedding_model


def generate_embedding(text: str, use_openai: bool = False) -> List[float]:
    """
    Generate embedding for text.
    
    Args:
        text: Text to embed
        use_openai: Whether to use OpenAI API (requires API key)
    
    Returns:
        List of floats representing the embedding
    """
    if use_openai and settings.openai_api_key:
        try:
            logger.info("Generating embedding using OpenAI")
            response = openai.embeddings.create(
                model=settings.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"OpenAI embedding failed: {e}. Falling back to local model.")
    
    # Use local model
    logger.info("Generating embedding using local model")
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()


def batch_generate_embeddings(texts: List[str], use_openai: bool = False) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of texts to embed
        use_openai: Whether to use OpenAI API
    
    Returns:
        List of embeddings
    """
    if use_openai and settings.openai_api_key:
        try:
            logger.info(f"Generating {len(texts)} embeddings using OpenAI")
            response = openai.embeddings.create(
                model=settings.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.warning(f"OpenAI batch embedding failed: {e}. Falling back to local model.")
    
    # Use local model
    logger.info(f"Generating {len(texts)} embeddings using local model")
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
    return [emb.tolist() for emb in embeddings]

