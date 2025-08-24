"""
Profile processing service for character profile management.
Contains the refactored logic from the original profile_refresher function.
"""
import logging
from typing import Dict, List, Any, Optional
from django.db import transaction


from ai_workflow.src.schemas.output_structures import Profile, Character
from ai_workflow.src.services.db_services import CharacterDBService
from ai_workflow.src.services.ai_services import AIChainService, EmbeddingService, EmbeddingCache
from ai_workflow.src.services.utils import (
    normalize_key, safe_str, safe_list, merge_list, merge_relations, 
    find_best_character_match, validate_profile_data, SIMILARITY_THRESHOLD
)
from books.models import Book

logger = logging.getLogger(__name__)


class ProfileProcessor:
    """Service for processing and updating character profiles."""
    
    def __init__(self, similarity_threshold: float = SIMILARITY_THRESHOLD):
        self.similarity_threshold = similarity_threshold
        self.embedding_cache = EmbeddingCache()
    
    def process_profile_updates(
        self, 
        last_profiles_by_name: Dict[str, List[Character]], 
        last_summary: str,
        book_id: str,
        character_names: List[str]
    ) -> Dict[str, List[Character]]:
        """
        Main entry point for processing profile updates.
        Refactored from the original profile_refresher function.
        """
        logger.info("Starting profile update processing")
        
        # 1. Prepare data structures
        pydantic_chars_by_name, django_chars_by_id = self._prepare_data_structures(
            last_profiles_by_name
        )
        
        # 2. Get AI-generated profile differences
        profile_diffs = self._get_profile_differences(
            last_summary, pydantic_chars_by_name, character_names
        )
        
        if not profile_diffs:
            logger.info("No profile differences found")
            return pydantic_chars_by_name
        
        # 3. Build embedding cache for similarity matching
        self._build_embedding_cache(pydantic_chars_by_name)
        
        # 4. Process each profile update
        book = Book.objects.get(book_id=book_id)
        
        with transaction.atomic():
            for new_profile_data in profile_diffs.profiles:
                if not validate_profile_data(new_profile_data):
                    logger.warning(f"Invalid profile data: {new_profile_data}")
                    continue
                
                self._process_single_profile_update(
                    new_profile_data,
                    pydantic_chars_by_name,
                    django_chars_by_id,
                    book
                )
        
        logger.info("Profile update processing completed")
        return pydantic_chars_by_name
    
    def _prepare_data_structures(
        self, 
        last_profiles_by_name: Dict[str, List[Character]]
    ) -> tuple[Dict[str, List[Character]], Dict[str, Any]]:
        """
        Prepare data structures and fetch all required Django characters in bulk.
        Fixes the N+1 query problem from the original code.
        """
        logger.info("Preparing data structures for profile processing")
        
        # Copy pydantic characters
        pydantic_chars_by_name = {
            name: profiles[:] for name, profiles in last_profiles_by_name.items()
        }
        
        # Collect all character IDs for bulk fetching
        all_character_ids = [
            pydantic_char.id 
            for profiles in pydantic_chars_by_name.values() 
            for pydantic_char in profiles
        ]
        
        # Bulk fetch all Django characters (fixes N+1 query problem)
        django_chars_by_id = CharacterDBService.get_characters_by_ids(all_character_ids)
        
        logger.info(f"Prepared {len(all_character_ids)} characters for processing")
        return pydantic_chars_by_name, django_chars_by_id
    
    def _get_profile_differences(
        self, 
        last_summary: str, 
        pydantic_chars_by_name: Dict[str, List[Character]], 
        character_names: List[str]
    ) -> Optional[Any]:
        """Get profile differences using AI chain."""
        logger.info("Getting profile differences from AI")
        
        flat_profiles = [
            char for profiles in pydantic_chars_by_name.values() 
            for char in profiles
        ]
        
        profile_dicts = [char.profile.model_dump() for char in flat_profiles]
        
        return AIChainService.get_profile_differences(
            last_summary, profile_dicts, character_names
        )
    
    def _build_embedding_cache(self, pydantic_chars_by_name: Dict[str, List[Character]]) -> None:
        """Build embedding cache for all existing characters."""
        logger.info("Building embedding cache for similarity matching")
        
        for key_name, profiles_list in pydantic_chars_by_name.items():
            for char in profiles_list:
                profile_text = EmbeddingService.profile_to_text(char.profile)
                self.embedding_cache.get_embedding(key_name, char.id, profile_text)
        
        logger.info("Embedding cache built successfully")
    
    def _process_single_profile_update(
        self,
        new_profile_data: Any,
        pydantic_chars_by_name: Dict[str, List[Character]],
        django_chars_by_id: Dict[str, Any],
        book: Book
    ) -> None:
        """Process a single profile update."""
        model_name_raw = safe_str(new_profile_data.name)
        logger.info(f"Processing profile update for: {model_name_raw}")
        
        # Find or create the character key
        matched_key = self._find_character_key(model_name_raw, pydantic_chars_by_name)
        
        if matched_key not in pydantic_chars_by_name:
            pydantic_chars_by_name[matched_key] = []
        
        pydantic_profiles_list = pydantic_chars_by_name[matched_key]
        
        # Find matching existing character
        matched_profile = self._find_matching_character(
            model_name_raw, new_profile_data, pydantic_profiles_list, matched_key
        )
        
        if matched_profile:
            # Update existing character
            self._update_existing_character(
                matched_profile, new_profile_data, model_name_raw,
                pydantic_profiles_list, django_chars_by_id
            )
        else:
            # Create new character
            self._create_new_character(
                new_profile_data, model_name_raw, book,
                pydantic_profiles_list, matched_key
            )
    
    def _find_character_key(
        self, 
        model_name_raw: str, 
        pydantic_chars_by_name: Dict[str, List[Character]]
    ) -> str:
        """Find the appropriate key for the character."""
        model_key_norm = normalize_key(model_name_raw)
        
        for key_name in pydantic_chars_by_name.keys():
            if normalize_key(key_name) == model_key_norm:
                return key_name
        
        return model_name_raw
    
    def _find_matching_character(
        self,
        model_name_raw: str,
        new_profile_data: Any,
        pydantic_profiles_list: List[Character],
        matched_key: str
    ) -> Optional[Character]:
        """Find matching character using name matching and similarity."""
        if not pydantic_profiles_list:
            return None
        
        new_name_norm = normalize_key(model_name_raw)
        
        # First try exact name matching
        for existing_char in pydantic_profiles_list:
            names_to_check = [existing_char.profile.name] + safe_list(existing_char.profile.aliases)
            names_norm = [normalize_key(name) for name in names_to_check]
            if new_name_norm in names_norm:
                logger.info(f"Found exact name match for {model_name_raw}")
                return existing_char
        
        # If no exact match, use similarity matching
        return self._find_similar_character(new_profile_data, pydantic_profiles_list, matched_key)
    
    def _find_similar_character(
        self,
        new_profile_data: Any,
        pydantic_profiles_list: List[Character],
        matched_key: str
    ) -> Optional[Character]:
        """Find similar character using embedding similarity."""
        new_profile_text = EmbeddingService.profile_to_text(new_profile_data)
        new_embedding = EmbeddingService.get_embedding(new_profile_text)
        
        def similarity_func(candidate: Character) -> float:
            existing_embedding = self.embedding_cache.get_embedding(
                matched_key, candidate.id, 
                EmbeddingService.profile_to_text(candidate.profile)
            )
            return EmbeddingService.cosine_similarity(new_embedding, existing_embedding)
        
        best_match, similarity_score = find_best_character_match(
            new_profile_data.name, pydantic_profiles_list, 
            similarity_func, self.similarity_threshold
        )
        
        if best_match:
            logger.info(f"Found similar character match with score {similarity_score:.3f}")
        
        return best_match
    
    def _update_existing_character(
        self,
        existing_char: Character,
        new_profile_data: Any,
        model_name_raw: str,
        pydantic_profiles_list: List[Character],
        django_chars_by_id: Dict[str, Any]
    ) -> None:
        """Update an existing character with new profile data."""
        logger.info(f"Updating existing character: {existing_char.profile.name}")
        
        # Merge profile data
        merged_profile = self._merge_profiles(existing_char.profile, new_profile_data, model_name_raw)
        
        # Update Django model
        django_character = django_chars_by_id.get(existing_char.id)
        if django_character:
            CharacterDBService.update_character_profile(django_character, merged_profile)
        
        # Update Pydantic object in list
        char_index = pydantic_profiles_list.index(existing_char)
        pydantic_profiles_list[char_index] = Character(id=existing_char.id, profile=merged_profile)
    
    def _create_new_character(
        self,
        new_profile_data: Any,
        model_name_raw: str,
        book: Book,
        pydantic_profiles_list: List[Character],
        matched_key: str
    ) -> None:
        """Create a new character with the profile data."""
        logger.info(f"Creating new character: {model_name_raw}")
        
        merged_profile = Profile(
            name=safe_str(model_name_raw),
            age=safe_str(new_profile_data.age),
            role=safe_str(new_profile_data.role),
            events=safe_list(new_profile_data.events),
            relations=safe_list(new_profile_data.relations),
            aliases=safe_list(new_profile_data.aliases),
            physical_characteristics=safe_list(new_profile_data.physical_characteristics),
            personality=safe_list(new_profile_data.personality),
        )
        
        # Create Django character
        django_character = CharacterDBService.create_character(book, merged_profile)
        
        # Create Pydantic character and add to list
        pydantic_character = Character(id=str(django_character.character_id), profile=merged_profile)
        pydantic_profiles_list.append(pydantic_character)
        
        # Cache embedding for future similarity matching
        profile_text = EmbeddingService.profile_to_text(merged_profile)
        embedding = EmbeddingService.get_embedding(profile_text)
        self.embedding_cache.set_embedding(matched_key, str(django_character.character_id), embedding)
    
    def _merge_profiles(self, existing_profile: Profile, new_profile_data: Any, model_name_raw: str) -> Profile:
        """Merge existing profile with new profile data."""
        return Profile(
            name=safe_str(existing_profile.name),
            age=safe_str(new_profile_data.age or existing_profile.age),
            role=safe_str(new_profile_data.role or existing_profile.role),
            events=merge_list(existing_profile.events, new_profile_data.events),
            relations=merge_relations(existing_profile.relations, new_profile_data.relations),
            aliases=merge_list(
                existing_profile.aliases,
                [model_name_raw] if model_name_raw != existing_profile.name else []
            ),
            physical_characteristics=merge_list(
                existing_profile.physical_characteristics,
                new_profile_data.physical_characteristics
            ),
            personality=merge_list(
                existing_profile.personality,
                new_profile_data.personality
            ),
        )
