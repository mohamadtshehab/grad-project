"""
Django ORM adapter for character database operations.
This module provides a bridge between the AI workflow and Django models.
"""

import os
import sys
import django
import json
from typing import Dict, List, Optional, Any
from rapidfuzz import fuzz
import uuid


# Setup Django environment if not already configured
def setup_django():
    """Initialize Django settings for standalone scripts."""
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')
        django.setup()

# Initialize Django
setup_django()

# Now import Django models
from django.db import transaction
from characters.models import Character, CharacterRelationship
from books.models import Book
from chunks.models import Chunk
from ai_workflow.src.preprocessors.text_cleaners import normalize_arabic_characters
from ai_workflow.src.configs import FUZZY_MATCHING_CONFIG


class DjangoCharacterAdapter:
    """
    Adapter class that provides the same interface as CharacterDatabase
    but uses Django ORM models underneath.
    """
    
    def __init__(self, book_id: Optional[str] = None):
        """
        Initialize the adapter with an optional book context.
        
        Args:
            book_id: UUID of the book for character context
        """
        self.book_id = book_id
        self._book = None
    
    
    @property
    def book(self) -> Optional[Book]:
        """Get the current book instance."""
        if self.book_id and not self._book:
            try:
                self._book = Book.objects.get(book_id=self.book_id)
            except Book.DoesNotExist:
                pass
        return self._book
    
    def set_book(self, book_id: str) -> None:
        """Set the book context for character operations."""
        self.book_id = book_id
        self._book = None  # Reset cached book
    
    def insert_character(self, profile: Dict[str, Any]) -> str:
        """
        Insert a new character profile into the database.
        
        Args:
            profile: Character profile as a dictionary (must contain 'name' field)
            
        Returns:
            The generated character_id as string
        """
        if 'name' not in profile:
            raise ValueError("Profile must contain a 'name' field")
        
        if not self.book_id:
            raise ValueError("Book ID is required to create a character. Please provide book_id when creating the adapter.")
        
        if not self.book:
            raise ValueError(f"Book with ID '{self.book_id}' not found in database. Please ensure the book exists.")
        

        with transaction.atomic():
            character = Character.objects.create(
                book_id=self.book,
                character_data=profile
            )
                    
        return str(character.character_id)
    
    def update_character(self, id: str, profile: Dict[str, Any]) -> bool:
        """
        Update an existing character profile.
        
        Args:
            id: The character's unique ID
            profile: Updated character profile
            
        Returns:
            True if update was successful, False if character not found
        """
        try:

            with transaction.atomic():
                character = Character.objects.get(character_id=id)
                
                
                character.character_data = profile
                character.save()
                
            return True
        except Character.DoesNotExist:
            return False
    
    def get_character(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a character profile by ID.
        
        Args:
            id: The character's unique ID
            
        Returns:
            Character profile as dictionary, or None if not found
        """
        try:
            character = Character.objects.get(character_id=id)
            return {
                'id': str(character.character_id),
                'profile': character.character_data
            }
        except Character.DoesNotExist:
            return None
    
    def find_characters_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Find characters by name (handles multiple characters with same name).
        
        Args:
            name: Character name to search for
            
        Returns:
            List of character profiles
        """
        queryset = Character.objects.all()
        
        # Filter by book if context is set
        if self.book:
            queryset = queryset.filter(book_id=self.book)
        
        # Use Django's JSON field lookup
        queryset = queryset.filter(character_data__name__icontains=name)
        
        characters = []
        for character in queryset:
            characters.append({
                'id': str(character.character_id),
                'profile': character.character_data
            })
        
        return characters
    
    def find_characters_by_name_enhanced(
        self, 
        name: str, 
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Enhanced character search using fuzzy matching.
        
        Args:
            name: Character name to search for
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of character profiles with confidence scores
        """
        # Get all characters for fuzzy matching
        all_characters = self.get_all_characters()
        
        # Normalize search name
        normalized_search_name = normalize_arabic_characters(name)
        
        # Prepare candidates for fuzzy matching
        candidates = []
        for char in all_characters:
            char_name = char['profile'].get('name', '')
            
            # Normalize stored name
            normalized_char_name = normalize_arabic_characters(char_name)
            
            # Calculate name similarity
            name_similarity = fuzz.ratio(normalized_search_name, normalized_char_name) / 100.0
            
            # Combined similarity score using configured weights
            score = (name_similarity * FUZZY_MATCHING_CONFIG['weights']['name_similarity'])
            
            if score >= similarity_threshold:
                candidates.append({
                    **char,
                    'similarity_score': score,
                    'name_similarity': name_similarity,
                })
        
        # Sort by similarity score (highest first)
        candidates.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return candidates
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """
        Retrieve all character profiles.
        
        Returns:
            List of all character profiles
        """
        queryset = Character.objects.all()
        
        # Filter by book if context is set
        if self.book:
            queryset = queryset.filter(book_id=self.book)
        
        # Order by name in character_data
        queryset = queryset.order_by('character_data__name')
        
        characters = []
        for character in queryset:
            characters.append({
                'id': str(character.character_id),
                'profile': character.character_data
            })
        
        return characters
    
    def delete_character(self, id: str) -> bool:
        """
        Delete a character profile.
        
        Args:
            id: The character's unique ID
            
        Returns:
            True if deletion was successful, False if character not found
        """
        try:
            with transaction.atomic():
                character = Character.objects.get(character_id=id)
                character.delete()
            return True
        except Character.DoesNotExist:
            return False
    
    def search_characters(self, query: str) -> List[Dict[str, Any]]:
        """
        Search characters by name in profile JSON.
        
        Args:
            query: Search query
            
        Returns:
            List of matching character profiles
        """
        queryset = Character.objects.all()
        
        # Filter by book if context is set
        if self.book:
            queryset = queryset.filter(book_id=self.book)
        
        # Search in character_data JSON field
        queryset = queryset.filter(character_data__name__icontains=query)
        queryset = queryset.order_by('character_data__name')
        
        characters = []
        for character in queryset:
            characters.append({
                'id': str(character.character_id),
                'profile': character.character_data
            })
        
        return characters
    
    def get_character_count(self) -> int:
        """
        Get the total number of characters in the database.
        
        Returns:
            Number of characters
        """
        queryset = Character.objects.all()
        
        # Filter by book if context is set
        if self.book:
            queryset = queryset.filter(book_id=self.book)
        
        return queryset.count()
    
    def clear_database(self):
        """Clear all character data from the database."""
        with transaction.atomic():
            if self.book:
                # Clear only characters for the current book
                Character.objects.filter(book_id=self.book).delete()
            else:
                # Clear all characters (use with caution!)
                Character.objects.all().delete()
    
    def create_character_relationship(
        self,
        character_id_1: str,
        character_id_2: str,
        relationship_type: str,
        description: str = ""
    ) -> Optional[CharacterRelationship]:
        """
        Create a relationship between two characters.
        
        Args:
            character_id_1: First character ID
            character_id_2: Second character ID
            relationship_type: Type of relationship
            description: Optional description
            
        Returns:
            Created relationship or None if characters don't exist
        """
        if not self.book:
            raise ValueError("Book context is required to create character relationships")
        
        try:
            with transaction.atomic():
                char1 = Character.objects.get(character_id=character_id_1)
                char2 = Character.objects.get(character_id=character_id_2)
                
                relationship, created = CharacterRelationship.objects.get_or_create(
                    character_id_1=char1,
                    character_id_2=char2,
                    book_id=self.book,
                    defaults={
                        'relationship_type': relationship_type,
                        'description': description
                    }
                )
                
                if not created:
                    # Update existing relationship
                    relationship.relationship_type = relationship_type
                    relationship.description = description
                    relationship.save()
                
                return relationship
        except Character.DoesNotExist:
            return None


# Global adapter instance (will be initialized with book context when needed)
character_adapter = None


def get_character_adapter(book_id: Optional[str] = None) -> DjangoCharacterAdapter:
    """
    Get the character adapter instance.
    
    Args:
        book_id: Optional book ID to set as context
        
    Returns:
        DjangoCharacterAdapter instance
    """
    global character_adapter
    
    if character_adapter is None:
        character_adapter = DjangoCharacterAdapter(book_id)
    elif book_id:
        character_adapter.set_book(book_id)
    
    return character_adapter
