"""
Test suite for Django ORM integration with AI workflow.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Setup Django environment
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')

import django
django.setup()

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from books.models import Book
from characters.models import Character, CharacterRelationship
from ai_workflow.src.databases.django_adapter import DjangoCharacterAdapter, get_character_adapter
from ai_workflow.src.django_integration import process_book_with_ai_workflow
from ai_workflow.src.schemas.states import create_initial_state

User = get_user_model()


class DjangoCharacterAdapterTestCase(TransactionTestCase):
    """Test cases for DjangoCharacterAdapter."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create a test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            user_id=self.user
        )
        
        # Initialize adapter with book context
        self.adapter = DjangoCharacterAdapter(str(self.book.book_id))
    
    def test_adapter_initialization(self):
        """Test adapter initialization with book context."""
        self.assertIsNotNone(self.adapter)
        self.assertEqual(self.adapter.book_id, str(self.book.book_id))
        self.assertEqual(self.adapter.book, self.book)
    
    def test_insert_character(self):
        """Test inserting a new character."""
        profile = {
            'name': 'أحمد',
            'age': 30,
            'role': 'protagonist',
            'personality': 'brave and intelligent'
        }
        
        character_id = self.adapter.insert_character(profile)
        
        self.assertIsNotNone(character_id)
        
        # Verify character was created in database
        character = Character.objects.get(character_id=character_id)
        self.assertEqual(character.name, 'أحمد')
        self.assertEqual(character.character_data['age'], 30)
        self.assertEqual(character.book_id, self.book)
    
    def test_insert_character_without_name(self):
        """Test inserting a character without a name raises error."""
        profile = {
            'age': 30,
            'role': 'protagonist'
        }
        
        with self.assertRaises(ValueError) as context:
            self.adapter.insert_character(profile)
        
        self.assertIn("name", str(context.exception))
    
    def test_update_character(self):
        """Test updating an existing character."""
        # Create a character first
        profile = {'name': 'سارة', 'age': 25}
        character_id = self.adapter.insert_character(profile)
        
        # Update the character
        updated_profile = {
            'name': 'سارة',
            'age': 26,
            'role': 'supporting character',
            'personality': 'kind and helpful'
        }
        
        success = self.adapter.update_character(character_id, updated_profile)
        
        self.assertTrue(success)
        
        # Verify update in database
        character = Character.objects.get(character_id=character_id)
        self.assertEqual(character.character_data['age'], 26)
        self.assertEqual(character.character_data['role'], 'supporting character')
    
    def test_get_character(self):
        """Test retrieving a character by ID."""
        # Create a character
        profile = {'name': 'محمد', 'age': 35, 'role': 'mentor'}
        character_id = self.adapter.insert_character(profile)
        
        # Retrieve the character
        result = self.adapter.get_character(character_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], character_id)
        self.assertEqual(result['profile']['name'], 'محمد')
        self.assertEqual(result['profile']['age'], 35)
    
    def test_find_characters_by_name(self):
        """Test finding characters by name."""
        # Create multiple characters
        self.adapter.insert_character({'name': 'علي', 'age': 30})
        self.adapter.insert_character({'name': 'علي', 'age': 45})  # Same name, different age
        self.adapter.insert_character({'name': 'فاطمة', 'age': 28})
        
        # Find characters named 'علي'
        results = self.adapter.find_characters_by_name('علي')
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result['profile']['name'], 'علي')
    
    def test_find_characters_by_name_enhanced(self):
        """Test enhanced character search with fuzzy matching."""
        # Create characters with similar names
        self.adapter.insert_character({'name': 'أحمد', 'age': 30})
        self.adapter.insert_character({'name': 'احمد', 'age': 25})  # Without hamza
        self.adapter.insert_character({'name': 'أحمـد', 'age': 35})  # With different encoding
        
        # Search with fuzzy matching
        results = self.adapter.find_characters_by_name_enhanced('احمد', similarity_threshold=0.7)
        
        # Should find all variations
        self.assertGreaterEqual(len(results), 2)
        
        # Check similarity scores
        for result in results:
            self.assertIn('similarity_score', result)
            self.assertGreaterEqual(result['similarity_score'], 0.7)
    
    def test_get_all_characters(self):
        """Test retrieving all characters."""
        # Create multiple characters
        names = ['زينب', 'عمر', 'ليلى']
        for name in names:
            self.adapter.insert_character({'name': name})
        
        # Get all characters
        results = self.adapter.get_all_characters()
        
        self.assertEqual(len(results), 3)
        result_names = [r['profile']['name'] for r in results]
        for name in names:
            self.assertIn(name, result_names)
    
    def test_delete_character(self):
        """Test deleting a character."""
        # Create a character
        profile = {'name': 'ياسر', 'age': 40}
        character_id = self.adapter.insert_character(profile)
        
        # Delete the character
        success = self.adapter.delete_character(character_id)
        
        self.assertTrue(success)
        
        # Verify deletion
        self.assertFalse(Character.objects.filter(character_id=character_id).exists())
        
        # Try to get deleted character
        result = self.adapter.get_character(character_id)
        self.assertIsNone(result)
    
    def test_search_characters(self):
        """Test searching characters by query."""
        # Create characters
        self.adapter.insert_character({'name': 'عبد الله', 'age': 30})
        self.adapter.insert_character({'name': 'عبد الرحمن', 'age': 35})
        self.adapter.insert_character({'name': 'محمد', 'age': 28})
        
        # Search for characters with 'عبد' in their name
        results = self.adapter.search_characters('عبد')
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn('عبد', result['profile']['name'])
    
    def test_get_character_count(self):
        """Test getting character count."""
        # Initially should be 0
        self.assertEqual(self.adapter.get_character_count(), 0)
        
        # Add characters
        self.adapter.insert_character({'name': 'خالد'})
        self.adapter.insert_character({'name': 'نور'})
        
        # Count should be 2
        self.assertEqual(self.adapter.get_character_count(), 2)
    
    def test_clear_database(self):
        """Test clearing characters for a book."""
        # Create characters
        self.adapter.insert_character({'name': 'سمير'})
        self.adapter.insert_character({'name': 'هدى'})
        
        # Clear database
        self.adapter.clear_database()
        
        # Should have no characters
        self.assertEqual(self.adapter.get_character_count(), 0)
    
    def test_create_character_relationship(self):
        """Test creating relationships between characters."""
        # Create two characters
        char1_id = self.adapter.insert_character({'name': 'رامي'})
        char2_id = self.adapter.insert_character({'name': 'سلمى'})
        
        # Create a relationship
        relationship = self.adapter.create_character_relationship(
            char1_id,
            char2_id,
            'friend',
            'Best friends since childhood'
        )
        
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.relationship_type, 'friend')
        self.assertEqual(relationship.description, 'Best friends since childhood')
    
    def test_book_context_isolation(self):
        """Test that characters are isolated by book context."""
        # Create another book
        book2 = Book.objects.create(
            title='Another Book',
            author='Another Author',
            user_id=self.user
        )
        
        # Add character to first book
        self.adapter.insert_character({'name': 'كريم'})
        
        # Switch to second book context
        adapter2 = DjangoCharacterAdapter(str(book2.book_id))
        
        # Add character to second book
        adapter2.insert_character({'name': 'منى'})
        
        # Each adapter should only see its own book's characters
        self.assertEqual(self.adapter.get_character_count(), 1)
        self.assertEqual(adapter2.get_character_count(), 1)
        
        # Verify names
        chars1 = self.adapter.get_all_characters()
        chars2 = adapter2.get_all_characters()
        
        self.assertEqual(chars1[0]['profile']['name'], 'كريم')
        self.assertEqual(chars2[0]['profile']['name'], 'منى')


class StateManagementTestCase(TestCase):
    """Test cases for state management without CharacterDatabase."""
    
    def test_create_initial_state_without_book(self):
        """Test creating initial state without book context."""
        state = create_initial_state()
        
        self.assertIsNone(state['book_id'])
        self.assertIsNotNone(state['file_path'])
        self.assertEqual(state['cleaned_text'], '')
        self.assertEqual(state['content_text'], '')
        self.assertIsNone(state['last_profiles'])
        self.assertIsNone(state['last_appearing_names'])
    
    def test_create_initial_state_with_book(self):
        """Test creating initial state with book context."""
        book_id = 'test-book-id-123'
        file_path = 'test/path/to/file.txt'
        
        state = create_initial_state(book_id=book_id, file_path=file_path)
        
        self.assertEqual(state['book_id'], book_id)
        self.assertEqual(state['file_path'], file_path)
    
    def test_state_no_database_field(self):
        """Test that state doesn't have database field anymore."""
        state = create_initial_state()
        
        # Should not have 'database' key
        self.assertNotIn('database', state)
        
        # Should have 'book_id' key instead
        self.assertIn('book_id', state)


class GetCharacterAdapterTestCase(TestCase):
    """Test cases for get_character_adapter function."""
    
    def test_get_adapter_singleton(self):
        """Test that get_character_adapter returns singleton."""
        adapter1 = get_character_adapter()
        adapter2 = get_character_adapter()
        
        # Should be the same instance
        self.assertIs(adapter1, adapter2)
    
    def test_get_adapter_with_book_id(self):
        """Test getting adapter with book ID."""
        book_id = 'test-book-123'
        adapter = get_character_adapter(book_id)
        
        self.assertEqual(adapter.book_id, book_id)
    
    def test_adapter_book_context_update(self):
        """Test updating adapter's book context."""
        # Get adapter without book
        adapter = get_character_adapter()
        self.assertIsNone(adapter.book_id)
        
        # Update with book ID
        book_id = 'new-book-456'
        adapter = get_character_adapter(book_id)
        self.assertEqual(adapter.book_id, book_id)


if __name__ == '__main__':
    unittest.main()
