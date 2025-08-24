"""
Database services module for character and relationship management.
Handles all database operations with optimized bulk queries.
"""
import logging
from typing import Dict, List
from django.db import transaction
from django.db.models import Q

from characters.models import Character as CharacterModel, CharacterRelationship, ChunkCharacter
from books.models import Book
from chunks.models import Chunk
from ai_workflow.src.schemas.output_structures import Profile, Character
from typing import Optional

logger = logging.getLogger(__name__)

class ChunkDBService:
    """Service class for chunk-related database operations."""
    
    @staticmethod
    def get_chunk_id_by_book_and_number(book_id: str, chunk_number: int) -> Optional[str]:
        """
        Retrieve a chunk_id by its book_id and chunk_number.
        
        Args:
            book_id: The UUID of the book
            chunk_number: The sequential number of the chunk within the book
            
        Returns:
            The chunk_id as a string if found, None otherwise
        """
        try:
            chunk = Chunk.objects.get(
                book_id=book_id,
                chunk_number=chunk_number
            )
            return str(chunk.chunk_id)
        except Chunk.DoesNotExist:
            return None

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
        
        characters = CharacterModel.objects.filter(character_id__in=character_ids)
        return {str(char.character_id): char for char in characters}
    
    @staticmethod
    def get_characters_by_names_and_book(book: Book, character_names: List[str]) -> Dict[str, List[CharacterModel]]:
        """
        Fetch characters by names for a specific book in a single query.
        Returns a mapping from name to list of matching CharacterModel instances.
        """
        if not character_names:
            return {}
        
        # Build Q objects for case-insensitive name matching
        name_queries = Q()
        for name in character_names:
            name_queries |= Q(profile__name__icontains=name)
        
        characters = CharacterModel.objects.filter(book=book).filter(name_queries)
        
        # Group characters by matching names
        result = {name: [] for name in character_names}
        for char in characters:
            char_name = char.profile.get('name', '')
            for search_name in character_names:
                if search_name.lower() in char_name.lower():
                    result[search_name].append(char)
                    break
        
        return result
    
    @staticmethod
    def create_character(book: Book, profile: Profile) -> CharacterModel:
        """Create a new character with the given profile."""
        return CharacterModel.objects.create(
            book=book,
            profile=profile.model_dump()
        )
    
    @staticmethod
    def update_character_profile(character: CharacterModel, profile: Profile) -> CharacterModel:
        """Update a character's profile and save to database."""
        character.profile = profile.model_dump()
        character.save()
        return character
    
    @staticmethod
    def bulk_update_characters(characters_and_profiles: List[tuple[CharacterModel, Profile]]) -> None:
        """Bulk update multiple characters with their new profiles."""
        with transaction.atomic():
            for character, profile in characters_and_profiles:
                character.profile = profile.model_dump()
            
            # Bulk update all characters
            CharacterModel.objects.bulk_update(
                [char for char, _ in characters_and_profiles], 
                ['profile']
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
            
            # Prepare bulk create/update operations
            relationships_to_create = []
            relationships_to_update = []
            
            for character_name in character_names:
                matching_characters = characters_by_name.get(character_name, [])
                
                for character in matching_characters:
                    # Check if relationship already exists
                    existing_rel = ChunkCharacter.objects.filter(
                        chunk=chunk, 
                        character=character
                    ).first()
                    
                    if existing_rel:
                        existing_rel.mention_count += 1
                        relationships_to_update.append(existing_rel)
                        logger.info(f"Updated mention count for '{character_name}' in chunk {chunk_number}")
                    else:
                        relationships_to_create.append(
                            ChunkCharacter(
                                chunk=chunk,
                                character=character,
                                mention_count=1,
                                position_info=None
                            )
                        )
                        logger.info(f"Linked character '{character_name}' to chunk {chunk_number}")
                
                if not matching_characters:
                    logger.warning(f"Character '{character_name}' not found for chunk {chunk_number}")
            
            # Bulk operations
            if relationships_to_create:
                ChunkCharacter.objects.bulk_create(relationships_to_create, ignore_conflicts=True)
            
            if relationships_to_update:
                ChunkCharacter.objects.bulk_update(relationships_to_update, ['mention_count'])
                
        except Chunk.DoesNotExist:
            logger.warning(f"Chunk {chunk_number} not found in database")


class CharacterRelationshipService:
    """Service class for character relationship operations."""
    
    @staticmethod
    def store_character_relationships(book: Book, profiles: List[Profile]) -> tuple[int, int]:
        """
        Extract and store character relationships from profiles.
        Returns (relationships_created, relationships_skipped).
        """
        relationships_created = 0
        relationships_skipped = 0
        
        # Get all character names mentioned in relationships
        all_character_names = set()
        for profile in profiles:
            all_character_names.add(profile.name)
            for relation in profile.relations or []:
                if ':' in relation:
                    other_name = relation.split(':', 1)[0].strip()
                    all_character_names.add(other_name)
        
        # Fetch all characters in a single query
        characters_by_name = {}
        if all_character_names:
            characters = CharacterModel.objects.filter(
                book=book,
                profile__name__in=list(all_character_names)
            )
            for char in characters:
                char_name = char.profile.get('name', '')
                characters_by_name[char_name] = char
        
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
                    if str(character.character_id) < str(other_character.character_id):
                        from_char, to_char = character, other_character
                    else:
                        from_char, to_char = other_character, character
                    
                    relationship, created = CharacterRelationship.objects.update_or_create(
                        from_character=from_char,
                        to_character=to_char,
                        book=book,
                        defaults={
                            'relationship_type': relationship_type,
                            'description': f"Relationship from {profile.name} to {other_name}"
                        }
                    )
                    
                    if created:
                        relationships_created += 1
                        logger.info(f"✓ Created relationship: {from_char.profile['name']} <-> {to_char.profile['name']} ({relationship_type})")
                    else:
                        logger.info(f"↻ Updated relationship: {from_char.profile['name']} <-> {to_char.profile['name']} ({relationship_type})")
        
        logger.info(f"Relationship processing complete: {relationships_created} created, {relationships_skipped} skipped")
        return relationships_created, relationships_skipped


def django_to_pydantic_character(django_char: CharacterModel) -> Character:
    """Convert Django Character model to Pydantic Character."""
    return Character(
        id=str(django_char.character_id),
        profile=Profile(**django_char.profile)
    )


def update_django_from_pydantic(django_char: CharacterModel, pydantic_profile: Profile) -> CharacterModel:
    """Update Django model from Pydantic profile."""
    django_char.profile = pydantic_profile.model_dump()
    django_char.save()
    return django_char
