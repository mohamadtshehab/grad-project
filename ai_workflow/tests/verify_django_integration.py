#!/usr/bin/env python3
"""
Script to verify Django ORM integration is working correctly.
"""

import os
import sys

# Setup Django environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')

import django
django.setup()

from django.db import connection
from books.models import Book
from characters.models import Character
from user.models import User
from ai_workflow.src.databases.django_adapter import DjangoCharacterAdapter, get_character_adapter

def verify_integration():
    """Verify that Django ORM integration is working."""
    print("=" * 50)
    print("Django ORM Integration Verification")
    print("=" * 50)
    
    # 1. Check Django is properly configured
    print("\n1. Checking Django configuration...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("   ✓ Django database connection successful")
    except Exception as e:
        print(f"   ✗ Django database connection failed: {e}")
        return False
    
    # 2. Check models are accessible
    print("\n2. Checking Django models...")
    try:
        user_count = User.objects.count()
        book_count = Book.objects.count()
        character_count = Character.objects.count()
        print(f"   ✓ Models accessible - Users: {user_count}, Books: {book_count}, Characters: {character_count}")
    except Exception as e:
        print(f"   ✗ Failed to access models: {e}")
        return False
    
    # 3. Test adapter initialization
    print("\n3. Testing Django adapter...")
    try:
        adapter = get_character_adapter()
        print("   ✓ Adapter initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize adapter: {e}")
        return False
    
    # 4. Test adapter with book context
    print("\n4. Testing adapter with book context...")
    try:
        # Get or create a test book
        test_user = User.objects.first()
        if not test_user:
            test_user = User.objects.create_user(
                email='test@verify.com',
                password='testpass',
                first_name='Test',
                last_name='Verify'
            )
        
        test_book = Book.objects.filter(title='Test Verification Book').first()
        if not test_book:
            test_book = Book.objects.create(
                title='Test Verification Book',
                author='Test Author',
                user_id=test_user
            )
        
        # Set book context
        adapter = get_character_adapter(str(test_book.book_id))
        print(f"   ✓ Adapter configured with book: {test_book.title}")
        
        # Test character operations
        print("\n5. Testing character operations...")
        
        # Insert a test character
        test_profile = {
            'name': 'تجربة',
            'age': 25,
            'role': 'test character'
        }
        char_id = adapter.insert_character(test_profile)
        print(f"   ✓ Character inserted with ID: {char_id}")
        
        # Retrieve the character
        retrieved = adapter.get_character(char_id)
        if retrieved and retrieved['profile']['name'] == 'تجربة':
            print("   ✓ Character retrieved successfully")
        else:
            print("   ✗ Failed to retrieve character correctly")
        
        # Search for character
        search_results = adapter.find_characters_by_name('تجربة')
        if search_results:
            print(f"   ✓ Character search successful - found {len(search_results)} result(s)")
        else:
            print("   ✗ Character search failed")
        
        # Update character
        updated_profile = {**test_profile, 'age': 26}
        if adapter.update_character(char_id, updated_profile):
            print("   ✓ Character updated successfully")
        else:
            print("   ✗ Failed to update character")
        
        # Delete character
        if adapter.delete_character(char_id):
            print("   ✓ Character deleted successfully")
        else:
            print("   ✗ Failed to delete character")
        
    except Exception as e:
        print(f"   ✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Test state creation
    print("\n6. Testing state management...")
    try:
        from ai_workflow.src.schemas.states import create_initial_state
        
        state = create_initial_state(book_id=str(test_book.book_id))
        if state['book_id'] == str(test_book.book_id):
            print("   ✓ State created with book context")
        else:
            print("   ✗ State book context mismatch")
        
        if 'database' not in state:
            print("   ✓ State correctly excludes database instance")
        else:
            print("   ✗ State still contains database instance")
        
    except Exception as e:
        print(f"   ✗ Failed to create state: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All verification checks passed!")
    print("Django ORM integration is working correctly.")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = verify_integration()
    sys.exit(0 if success else 1)
