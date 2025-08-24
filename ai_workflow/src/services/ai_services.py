"""
AI services module for external API interactions.
Centralizes API client management and caching.
"""
import logging
from functools import lru_cache
from typing import Dict, Any
import numpy as np
import cohere
from dotenv import load_dotenv


from ai_workflow.src.language_models.chains import (
    name_query_chain, 
    profile_difference_chain, 
    summary_chain, 
    empty_profile_validation_chain
)
from ai_workflow.src.schemas.output_structures import Profile

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize clients once when module is imported
try:
    COHERE_CLIENT = cohere.Client()
    logger.info("Cohere client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Cohere client: {e}")
    COHERE_CLIENT = None


class EmbeddingService:
    """Service for generating text embeddings."""
    
    @staticmethod
    @lru_cache(maxsize=1000)  # Cache embeddings for the same text
    def get_embedding(text: str) -> np.ndarray:
        """
        Generate an embedding for the given text using Cohere.
        Results are cached to avoid redundant API calls.
        """
        if not COHERE_CLIENT:
            raise RuntimeError("Cohere client not initialized")
        
        try:
            response = COHERE_CLIENT.embed(model="small", texts=[text])
            return np.array(response.embeddings[0])
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            raise
    
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)
    
    @staticmethod
    def profile_to_text(profile: Profile) -> str:
        """Convert a profile to a text representation for embedding."""
        return (f"{profile.name} | {profile.role or ''} | "
                f"events: {', '.join(profile.events or [])} | "
                f"relations: {', '.join(profile.relations or [])} | "
                f"personality: {', '.join(profile.personality or [])} | "
                f"aliases: {', '.join(profile.aliases or [])}")


class AIChainService:
    """Service for interacting with LangChain AI chains."""
    
    @staticmethod
    def extract_character_names(text: str) -> list[str]:
        """Extract character names from text using AI chain."""
        try:
            chain_input = {"text": str(text)}
            response = name_query_chain.invoke(chain_input)
            return response.names if hasattr(response, 'names') else []
        except Exception as e:
            logger.error(f"Failed to extract character names: {e}")
            return []
    
    @staticmethod
    def get_profile_differences(text: str, profiles: list[Dict[str, Any]], character_names: list[str]) -> Any:
        """Get profile differences using AI chain."""
        try:
            chain_input = {
                "text": text,
                "profiles": profiles,
                "list_of_character_name": character_names,
            }
            response = profile_difference_chain.invoke(chain_input)
            return response if response and hasattr(response, "profiles") else None
        except Exception as e:
            logger.error(f"Failed to get profile differences: {e}")
            return None
    
    @staticmethod
    def generate_summary(text: str, character_names: list[str]) -> str:
        """Generate summary using AI chain."""
        try:
            chain_input = {
                "text": text,
                "names": str(character_names)
            }
            response = summary_chain.invoke(chain_input)
            
            if not response or not hasattr(response, 'summary'):
                logger.warning("API response blocked for prohibited content")
                return None
            
            return response.summary
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None
    
    @staticmethod
    def validate_empty_profiles(text: str, profiles: list[str]) -> Any:
        """Validate empty profiles using AI chain."""
        try:
            chain_input = {
                "text": str(text),
                "profiles": str(profiles)
            }
            response = empty_profile_validation_chain.invoke(chain_input)
            return response
        except Exception as e:
            logger.error(f"Failed to validate empty profiles: {e}")
            return None


class EmbeddingCache:
    """Cache for storing and managing embeddings."""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, np.ndarray]] = {}
    
    def get_embedding(self, key: str, item_id: str, text: str) -> np.ndarray:
        """Get embedding from cache or generate new one."""
        if key not in self.cache:
            self.cache[key] = {}
        
        if item_id not in self.cache[key]:
            self.cache[key][item_id] = EmbeddingService.get_embedding(text)
        
        return self.cache[key][item_id]
    
    def set_embedding(self, key: str, item_id: str, embedding: np.ndarray) -> None:
        """Set embedding in cache."""
        if key not in self.cache:
            self.cache[key] = {}
        self.cache[key][item_id] = embedding
    
    def clear(self) -> None:
        """Clear all cached embeddings."""
        self.cache.clear()
