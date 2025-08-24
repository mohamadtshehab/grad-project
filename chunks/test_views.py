from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from chunks.models import Chunk
from characters.models import Character, CharacterRelationship, ChunkCharacter
from books.models import Book
from user.models import User
import uuid


class ChunkRelationshipsViewTest(TestCase):
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
        
        # Create test chunks
        self.chunk1 = Chunk.objects.create(
            book=self.book,
            chunk_text='This is chunk 1 with some text.',
            chunk_number=1
        )
        
        self.chunk2 = Chunk.objects.create(
            book=self.book,
            chunk_text='This is chunk 2 with different text.',
            chunk_number=2
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
        
        # Create chunk-character relationships
        self.chunk_char1 = ChunkCharacter.objects.create(
            chunk=self.chunk1,
            character=self.character1,
            mention_count=2
        )
        
        self.chunk_char2 = ChunkCharacter.objects.create(
            chunk=self.chunk1,
            character=self.character2,
            mention_count=1
        )
        
        # Character 3 is only in chunk 2
        self.chunk_char3 = ChunkCharacter.objects.create(
            chunk=self.chunk2,
            character=self.character3,
            mention_count=1
        )
        
        # Create a relationship between character1 and character2 (both in chunk1)
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

    def test_chunk_relationships_endpoint(self):
        """Test that the chunk relationships endpoint returns correct data."""
        url = reverse('chunks:chunk-relationships', args=[str(self.chunk1.chunk_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('chunk_id', data)
        self.assertIn('book_id', data)
        self.assertIn('relationships', data)
        self.assertIn('total_relationships', data)
        self.assertIn('characters_in_chunk', data)
        
        # Check chunk and book IDs
        self.assertEqual(data['chunk_id'], str(self.chunk1.chunk_id))
        self.assertEqual(data['book_id'], str(self.book.book_id))
        
        # Check relationships
        self.assertEqual(data['total_relationships'], 1)
        self.assertEqual(len(data['relationships']), 1)
        
        relationship = data['relationships'][0]
        self.assertIn('from_character_name', relationship)
        self.assertIn('from_character_id', relationship)
        self.assertIn('to_character_name', relationship)
        self.assertIn('to_character_id', relationship)
        self.assertIn('relationship_type', relationship)
        self.assertIn('description', relationship)
        
        self.assertEqual(relationship['relationship_type'], 'friends')
        self.assertEqual(relationship['description'], 'Alice and Bob are friends')
        
        # Check that both characters are in the chunk
        self.assertIn(str(self.character1.character_id), data['characters_in_chunk'])
        self.assertIn(str(self.character2.character_id), data['characters_in_chunk'])
        self.assertEqual(len(data['characters_in_chunk']), 2)

    def test_chunk_with_no_relationships(self):
        """Test that a chunk with no character relationships returns empty list."""
        url = reverse('chunks:chunk-relationships', args=[str(self.chunk2.chunk_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_relationships'], 0)
        self.assertEqual(len(response.data['relationships']), 0)
        self.assertEqual(len(response.data['characters_in_chunk']), 1)  # Only character3

    def test_chunk_not_found(self):
        """Test that the endpoint returns 404 for non-existent chunk."""
        fake_id = uuid.uuid4()
        url = reverse('chunks:chunk-relationships', args=[str(fake_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_chunk_id_format(self):
        """Test that the endpoint returns 400 for invalid chunk ID format."""
        url = reverse('chunks:chunk-relationships', args=['invalid-uuid'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_chunk_with_no_characters(self):
        """Test that a chunk with no characters returns appropriate response."""
        # Create a chunk with no characters
        empty_chunk = Chunk.objects.create(
            book=self.book,
            chunk_text='This chunk has no characters.',
            chunk_number=3
        )
        
        url = reverse('chunks:chunk-relationships', args=[str(empty_chunk.chunk_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_relationships'], 0)
        self.assertEqual(len(response.data['relationships']), 0)
        self.assertEqual(len(response.data['characters_in_chunk']), 0)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'No characters found in this chunk')
