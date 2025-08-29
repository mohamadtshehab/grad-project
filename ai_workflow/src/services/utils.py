"""
Utility functions for text processing and data manipulation.
Contains helper functions used across the AI workflow.
"""
import re
import unicodedata
from typing import List, Any, Optional


# Constants
SIMILARITY_THRESHOLD = 0.9
HONORIFICS_REGEX = re.compile(
    r"^(?:ال)?(?:(?:شيخ)|(?:السيد)|(?:سيد)|(?:معلم)|(?:الحاج)|(?:الحاجة)|"
    r"(?:الدكتور)|(?:دكتور)|(?:د\.)|(?:الأستاذ)|(?:الاستاذ)|(?:استاذ))\s+"
)


def remove_diacritics(text: str) -> str:
    """Remove diacritics from Arabic text."""
    text = text.replace("ـ", "")  # Remove tatweel
    return "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


def normalize_key(name: str) -> str:
    """
    Normalize a character name for comparison.
    Removes diacritics, honorifics, and spaces.
    """
    if not name:
        return ""
    
    name = str(name).strip().lower()
    name = remove_diacritics(name)
    name = HONORIFICS_REGEX.sub("", name)
    name = name.replace(" ", "")
    return name


def safe_str(value: Any) -> str:
    """
    Safely convert value to string, handling None and null-like values.
    """
    if value is None or (isinstance(value, str) and value.strip().lower() in ["none", "null"]):
        return ""
    return value.strip() if isinstance(value, str) else str(value)


def safe_list(value: Any) -> List[Any]:
    """
    Safely convert value to list, handling None values.
    """
    if value is None:
        return []
    return value if isinstance(value, list) else []


def merge_list(old_list: Optional[List[str]], new_list: Optional[List[str]]) -> List[str]:
    """
    Merge two lists, removing duplicates and handling None values.
    """
    old_list = safe_list(old_list)
    new_list = safe_list(new_list)
    return list(set(old_list + new_list)) if new_list else old_list


def merge_relations(old_list: Optional[List[str]], new_list: Optional[List[str]]) -> List[str]:
    """
    Merge relationship lists, handling duplicates by character name.
    Format: "character_name: relationship_type"
    """
    old_list = safe_list(old_list)
    new_list = safe_list(new_list)
    
    merged = {}
    for rel in old_list + new_list:
        if ":" in rel:
            name, relation = map(str.strip, rel.split(":", 1))
            merged[name] = relation
    
    return [f"{name}: {relation}" for name, relation in merged.items()]


def find_best_character_match(
    target_name: str, 
    candidates: List[Any], 
    similarity_func, 
    threshold: float = SIMILARITY_THRESHOLD
) -> tuple[Optional[Any], float]:
    """
    Find the best character match using similarity scoring.
    
    Args:
        target_name: The name to match against
        candidates: List of candidate characters
        similarity_func: Function to calculate similarity score
        threshold: Minimum similarity threshold
    
    Returns:
        Tuple of (best_match, similarity_score) or (None, 0.0)
    """
    if not candidates:
        return None, 0.0
    
    best_match = None
    best_score = 0.0
    
    target_normalized = normalize_key(target_name)
    
    for candidate in candidates:
        # First try exact name matching
        candidate_names = []
        if hasattr(candidate, 'profile'):
            candidate_names.append(candidate.profile.name)
            candidate_names.extend(safe_list(candidate.profile.aliases))
        
        # Check for exact normalized matches first
        for name in candidate_names:
            if normalize_key(name) == target_normalized:
                return candidate, 1.0
        
        # If no exact match, use similarity function
        try:
            score = similarity_func(candidate)
            if score > best_score:
                best_score = score
                best_match = candidate
        except Exception:
            continue  # Skip if similarity calculation fails
    
    return (best_match, best_score) if best_score >= threshold else (None, 0.0)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def validate_profile_data(profile_data: Any) -> bool:
    """
    Validate that profile data has required fields.
    """
    if not profile_data:
        return False
    
    required_fields = ['name']
    for field in required_fields:
        if not hasattr(profile_data, field) or not getattr(profile_data, field):
            return False
    
    return True
<<<<<<< HEAD
=======


def get_summarizer_and_first_name_querier_context(state):
    chunk_num = state['chunk_num']
    all_chunks = state['clean_chunks']
    current_chunk = all_chunks[chunk_num]
    
    # Initialize context with the current chunk. This also handles the first chunk (index 0).
    context = str(current_chunk)

    # If it's not the first chunk, prepend context from the previous chunk.
    if chunk_num > 0:
        previous_chunk = all_chunks[chunk_num - 1]
        third_of_length = len(previous_chunk) // 3
        previous_chunk_context = str(previous_chunk[2 * third_of_length:])
        
        # Combine the context from the previous chunk with the current chunk.
        context = f"{previous_chunk_context}\n\n{current_chunk}"

    return context
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
