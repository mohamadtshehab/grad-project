from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from characters.models import Character, CharacterRelationship
from books.models import Book
from user.models import User
import uuid


class CharacterRelationshipsViewTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        
        # Create a test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            user=self.user,
            book_id=uuid.uuid4()
        )
        
        # Create test characters
        self.character1 = Character.objects.create(
            book=self.book,
            character_data={'name': 'Alice', 'age': 25}
        )
        
        self.character2 = Character.objects.create(
            book=self.book,
            character_data={'name': 'Bob', 'age': 30}
        )
        
        self.character3 = Character.objects.create(
            book=self.book,
            character_data={'name': 'Charlie', 'age': 35}
        )
        
        # Create a relationship between character1 and character2
        # Ensure canonical order (from.id < to.id)
        if str(self.character1.character_id) < str(self.character2.character_id):
            from_char, to_char = self.character1, self.character2
        else:
            from_char, to_char = self.character2, self.character1
            
        self.relationship = CharacterRelationship.objects.create(
            from_character=from_char,
            to_character=to_char,
            book=self.book,
            relationship_type='friends',
            description='Alice and Bob are friends'
        )

    def test_character_relationships_endpoint(self):
        """Test that the character relationships endpoint returns correct data."""
        url = reverse('characters:character-relationships', args=[self.character1.character_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('character_name', data)
        self.assertIn('relationships', data)
        self.assertIn('total_relationships', data)
        
        # Check character name
        self.assertEqual(data['character_name'], 'Alice')
        
        # Check relationships
        self.assertEqual(data['total_relationships'], 1)
        self.assertEqual(len(data['relationships']), 1)
        
        relationship = data['relationships'][0]
        self.assertIn('character_name', relationship)
        self.assertIn('character_id', relationship)
        self.assertIn('relationship_type', relationship)
        self.assertEqual(relationship['relationship_type'], 'friends')
        
        # Check that the other character's name and id are returned
        if self.character1 == self.relationship.from_character:
            expected_name = self.character2.name
            expected_id = str(self.character2.character_id)
        else:
            expected_name = self.character1.name
            expected_id = str(self.character1.character_id)
        self.assertEqual(relationship['character_name'], expected_name)
        self.assertEqual(relationship['character_id'], expected_id)

    def test_character_not_found(self):
        """Test that the endpoint returns 404 for non-existent character."""
        fake_id = uuid.uuid4()
        url = reverse('characters:character-relationships', args=[fake_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_character_with_no_relationships(self):
        """Test that a character with no relationships returns empty list."""
        url = reverse('characters:character-relationships', args=[self.character3.character_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_relationships'], 0)
        self.assertEqual(len(response.data['relationships']), 0)
        self.assertEqual(response.data['character_name'], 'Charlie')
