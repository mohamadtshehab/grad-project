#!/usr/bin/env python
"""
Simple test script to verify Django models are working
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')
django.setup()

from user.models import User
from books.models import Book
from chunks.models import Chunk
from characters.models import Character, ChunkCharacter, CharacterRelationship

def test_models():
    """Test that all models are working correctly"""
    print("🧪 Testing Django Models...")
    print("=" * 50)
    
    # Test User model
    print(f"👥 Users: {User.objects.count()}")
    if User.objects.exists():
        user = User.objects.first()
        print(f"   Sample user: {user.name} ({user.email})")
    
    # Test Book model
    print(f"📚 Books: {Book.objects.count()}")
    if Book.objects.exists():
        book = Book.objects.first()
        print(f"   Sample book: {book.title} by {book.author}")
        print(f"   File: {book.file.name if book.file else 'No file'}")
    
    # Test Chunk model
    print(f"📄 Chunks: {Chunk.objects.count()}")
    if Chunk.objects.exists():
        chunk = Chunk.objects.first()
        print(f"   Sample chunk: {chunk.chunk_number} from book '{chunk.book_id.title}'")
        print(f"   Text preview: {chunk.chunk_text[:100]}...")
    
    # Test Character model
    print(f"👤 Characters: {Character.objects.count()}")
    if Character.objects.exists():
        character = Character.objects.first()
        print(f"   Sample character: {character.name} in '{character.book_id.title}'")
        print(f"   Role: {character.role}")
        print(f"   Age: {character.age}")
    
    # Test ChunkCharacter model
    print(f"🔗 Chunk-Character relationships: {ChunkCharacter.objects.count()}")
    if ChunkCharacter.objects.exists():
        rel = ChunkCharacter.objects.first()
        print(f"   Sample relationship: {rel.character_id.name} mentioned {rel.mention_count} times in chunk {rel.chunk_id.chunk_number}")
    
    # Test CharacterRelationship model
    print(f"💕 Character relationships: {CharacterRelationship.objects.count()}")
    if CharacterRelationship.objects.exists():
        rel = CharacterRelationship.objects.first()
        print(f"   Sample relationship: {rel.character_id_1.name} - {rel.relationship_type} - {rel.character_id_2.name}")
    
    print("=" * 50)
    print("✅ All models are working correctly!")

if __name__ == "__main__":
    test_models()
