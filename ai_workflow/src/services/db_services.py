"""
Database services module for character and relationship management.
Handles all database operations with optimized bulk queries.
"""
import logging
from typing import Dict, List, Optional
from django.db import transaction
from django.db.models import Q

from characters.models import Character as CharacterModel, CharacterRelationship, ChunkCharacter
from books.models import Book
from chunks.models import Chunk
from ai_workflow.src.schemas.output_structures import Profile, Character

logger = logging.getLogger(__name__)

class ChunkDBService:
    """Service class for chunk-related database operations."""
    
    @staticmethod
    def get_chunk_id_by_book_and_number(book_id: Optional[str], chunk_number: int) -> str:
        """
        Retrieve a chunk_id by its book_id and chunk_number.
        
        Args:
            book_id: The UUID of the book
            chunk_number: The sequential number of the chunk within the book
            
        Returns:
            The chunk_id as a string if found, empty string otherwise
        """
        if not book_id:
            return ""
        try:
            chunk = Chunk.objects.get(
                book_id=book_id,
                chunk_number=chunk_number
            )
            return str(chunk.id)
        except Chunk.DoesNotExist:
            return ""

class CharacterDBService:
    """Service class for character database operations."""
    
    @staticmethod
    def get_characters_by_ids(character_ids: List[str]) -> Dict[str, CharacterModel]:
        """
        Fetch multiple characters from the DB in a single query.
        Returns a mapping from character_id to CharacterModel instance.
        """
        if not character_ids:
            return {}
        
        characters = CharacterModel.objects.filter(id__in=character_ids)
        return {str(char.id): char for char in characters}
    
    @staticmethod
    def get_characters_by_names_and_book(book: Book, character_names: List[str]) -> Dict[str, List[CharacterModel]]:
        """
        Fetch characters by names for a specific book using latest chunk-based profiles.
        Returns a mapping from name to list of matching CharacterModel instances (latest per character).
        """
        if not character_names:
            return {}
        
        # For each queried name, find matching characters by latest ChunkCharacter.character_profile
        result: Dict[str, List[CharacterModel]] = {name: [] for name in character_names}
        
        for search_name in character_names:
            # Fetch ChunkCharacter rows that match name (case-insensitive), within this book
            qs = (
                ChunkCharacter.objects
                .filter(character__book=book, character_profile__name__icontains=search_name)
                .select_related('character', 'chunk')
                .order_by('-chunk__chunk_number')
            )
            seen_character_ids: set[str] = set()
            for cc in qs:
                cid = str(cc.character.id)
                if cid in seen_character_ids:
                    continue
                result[search_name].append(cc.character)
                seen_character_ids.add(cid)
        
        return result
    
    @staticmethod
    def create_character_with_initial_chunk_profile(book: Book, chunk_number: int, profile: Profile) -> CharacterModel:
        """Create a new character and its initial chunk profile for the given chunk number."""
        character = CharacterModel.objects.create(
            book=book,
        )
        # Attach initial chunk profile in ChunkCharacter
        chunk = Chunk.objects.get(book=book, chunk_number=chunk_number)
        ChunkCharacter.objects.create(
            chunk=chunk,
            character=character,
            character_profile=profile.model_dump()
        )
        return character
    
    @staticmethod
    def upsert_chunk_profile(character: CharacterModel, book: Book, chunk_number: int, profile: Profile) -> None:
        """Create or update the character's profile for a specific chunk."""
        chunk = Chunk.objects.get(book=book, chunk_number=chunk_number)
        ChunkCharacter.objects.update_or_create(
            chunk=chunk,
            character=character,
            defaults={'character_profile': profile.model_dump()},
        )
    
    @staticmethod
    def bulk_upsert_chunk_profiles(book: Book, chunk_number: int, characters_and_profiles: List[tuple[CharacterModel, Profile]]) -> None:
        """Bulk create/update chunk profiles for a list of characters for a given chunk."""
        chunk = Chunk.objects.get(book=book, chunk_number=chunk_number)
        with transaction.atomic():
            for character, profile in characters_and_profiles:
                ChunkCharacter.objects.update_or_create(
                    chunk=chunk,
                    character=character,
                    defaults={'character_profile': profile.model_dump()},
                )


class ChunkCharacterService:
    """Service class for chunk-character relationship operations."""
    
    @staticmethod
    def store_chunk_character_relationships(book: Book, chunk_number: int, character_names: List[str]) -> None:
        """
        Store chunk-character relationships in the database.
        Optimized to minimize database queries.
        """
        try:
            # Get the chunk object
            chunk = Chunk.objects.get(book=book, chunk_number=chunk_number)
            
            # Get all characters by names in a single query
            characters_by_name = CharacterDBService.get_characters_by_names_and_book(book, character_names)
            
            # Prepare bulk create operations (unique_together prevents duplicates)
            relationships_to_create = []
            
            for character_name in character_names:
                matching_characters = characters_by_name.get(character_name, [])
                
                for character in matching_characters:
                    # Ensure a ChunkCharacter row exists (profile will be set elsewhere)
                    exists = ChunkCharacter.objects.filter(chunk=chunk, character=character).exists()
                    if not exists:
                        relationships_to_create.append(
                            ChunkCharacter(
                                chunk=chunk,
                                character=character,
                                character_profile={}
                            )
                        )
                        logger.info(f"Linked character '{character_name}' to chunk {chunk_number}")
                
                if not matching_characters:
                    logger.warning(f"Character '{character_name}' not found for chunk {chunk_number}")
            
            # Bulk operations
            if relationships_to_create:
                ChunkCharacter.objects.bulk_create(relationships_to_create, ignore_conflicts=True)
                
        except Chunk.DoesNotExist:
            logger.warning(f"Chunk {chunk_number} not found in database")


class CharacterRelationshipService:
    """Service class for character relationship operations."""
    
    @staticmethod
    def store_character_relationships(book: Book, chunk_number: int, profiles: List[Profile]) -> tuple[int, int]:
        """
        Extract and store character relationships from profiles.
        Returns (relationships_created, relationships_skipped).
        """
        relationships_created = 0
        relationships_skipped = 0
        
        # Resolve chunk
        try:
            chunk = Chunk.objects.get(book=book, chunk_number=chunk_number)
        except Chunk.DoesNotExist:
            logger.warning(f"Chunk {chunk_number} not found; skipping relationships storage")
            return 0, len(profiles)
        
        # Get all character names mentioned in relationships
        all_character_names = set()
        for profile in profiles:
            all_character_names.add(profile.name)
            for relation in profile.relations or []:
                if ':' in relation:
                    other_name = relation.split(':', 1)[0].strip()
                    all_character_names.add(other_name)
        
        # Fetch characters via latest chunk-based profiles across the book
        characters_by_name: Dict[str, CharacterModel] = {}
        if all_character_names:
            cc_qs = (
                ChunkCharacter.objects
                .filter(character__book=book, character_profile__name__in=list(all_character_names))
                .select_related('character')
                .order_by('-chunk__chunk_number')
            )
            seen: set[str] = set()
            for cc in cc_qs:
                if cc.character_profile and 'name' in cc.character_profile:
                    name = cc.character_profile.get('name')
                    cid = str(cc.character.id)
                    if name not in characters_by_name and cid not in seen:
                        characters_by_name[name] = cc.character
                        seen.add(cid)
        
        with transaction.atomic():
            for profile in profiles:
                if not profile.relations:
                    logger.info(f"No relationships found for character: {profile.name}")
                    continue
                
                logger.info(f"Processing relationships for character: {profile.name}")
                logger.info(f"Relations found: {profile.relations}")
                
                # Get the character instance
                character = characters_by_name.get(profile.name)
                if not character:
                    logger.warning(f"Character '{profile.name}' not found in database")
                    continue
                
                for relation in profile.relations:
                    if ':' not in relation:
                        logger.warning(f"Invalid relationship format (missing ':'): {relation}")
                        continue
                    
                    other_name, relationship_type = relation.split(':', 1)
                    other_name = other_name.strip()
                    relationship_type = relationship_type.strip()
                    
                    logger.info(f"Attempting to create relationship: {profile.name} -> {relationship_type} -> {other_name}")
                    
                    # Find the other character
                    other_character = characters_by_name.get(other_name)
                    if not other_character:
                        relationships_skipped += 1
                        logger.warning(f"Character '{other_name}' not found, skipping relationship")
                        continue
                    
                    # Create or update the relationship with canonical order
                    if str(character.id) < str(other_character.id):
                        from_char, to_char = character, other_character
                    else:
                        from_char, to_char = other_character, character
                    
                    relationship, created = CharacterRelationship.objects.update_or_create(
                        from_character=from_char,
                        to_character=to_char,
                        chunk=chunk,
                        defaults={
                            'relationship_type': relationship_type,
                            # description removed from model; keep minimal payload
                        }
                    )
                    
                    if created:
                        relationships_created += 1
                        logger.info(f"✓ Created relationship: {profile.name} <-> {other_name} ({relationship_type}) in chunk {chunk_number}")
                    else:
                        logger.info(f"↻ Updated relationship: {profile.name} <-> {other_name} ({relationship_type}) in chunk {chunk_number}")
        
        logger.info(f"Relationship processing complete: {relationships_created} created, {relationships_skipped} skipped")
        return relationships_created, relationships_skipped


def django_to_pydantic_character(django_char: CharacterModel) -> Character:
    """Convert Django Character model to Pydantic Character using latest chunk profile."""
    cc = (
        ChunkCharacter.objects
        .filter(character=django_char)
        .select_related('chunk')
        .order_by('-chunk__chunk_number')
        .first()
    )
    from ai_workflow.src.services.utils import safe_list, safe_str
    profile_dict = cc.character_profile if cc and cc.character_profile else {}
    return Character(
        id=str(django_char.id),
        profile=Profile(
            name=safe_str(profile_dict.get('name', '')),
            role=safe_str(profile_dict.get('role', '')),
            events=safe_list(profile_dict.get('events')),
            relations=safe_list(profile_dict.get('relations')),
            aliases=safe_list(profile_dict.get('aliases')),
            physical_characteristics=safe_list(profile_dict.get('physical_characteristics')),
            personality=safe_list(profile_dict.get('personality')),
        )
    )


def update_django_from_pydantic(django_char: CharacterModel, pydantic_profile: Profile) -> CharacterModel:
    """Deprecated: profiles are chunk-based; use CharacterDBService.upsert_chunk_profile instead."""
    return django_char
