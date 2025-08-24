"""
Database service functions for AI workflow operations.
"""

from chunks.models import Chunk
from characters.models import Character, CharacterRelationship, ChunkCharacter
from books.models import Book
from typing import Optional, List


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
    """Service class for character-related database operations."""
    
    @staticmethod
    def get_characters_by_ids(character_ids: List[str]) -> List[Character]:
        """
        Retrieve characters by their IDs.
        
        Args:
            character_ids: List of character UUIDs
            
        Returns:
            List of Character objects
        """
        return list(Character.objects.filter(character_id__in=character_ids))
    
    @staticmethod
    def update_character_profile(django_character: Character, profile_data: dict) -> None:
        """
        Update a character's profile data.
        
        Args:
            django_character: The Django Character model instance
            profile_data: Dictionary containing the profile data
        """
        django_character.character_data = profile_data
        django_character.save()
    
    @staticmethod
    def create_character(book: Book, profile_data: dict) -> Character:
        """
        Create a new character.
        
        Args:
            book: The Book instance
            profile_data: Dictionary containing the profile data
            
        Returns:
            The created Character instance
        """
        return Character.objects.create(
            book=book,
            character_data=profile_data
        )
