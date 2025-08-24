# AI Workflow Django ORM Migration Guide

## Overview

This document describes the migration from the manual SQLite `CharacterDatabase` implementation to Django ORM models. The migration preserves all existing functionality while providing better integration with the Django application.

## Key Changes

### 1. Database Implementation
- **Old**: Manual SQLite database with JSON storage (`ai_workflow/src/databases/database.py`)
- **New**: Django ORM adapter (`ai_workflow/src/databases/django_adapter.py`) using Django models

### 2. State Management
- **Old**: State contained a `CharacterDatabase` instance
- **New**: State contains a `book_id` for context, no database instance

### 3. Character Operations
All database operations now use Django ORM:

| Old Method | New Method |
|------------|------------|
| `character_db.insert_character()` | `Character.objects.create()` or `adapter.insert_character()` |
| `character_db.get_character()` | `Character.objects.get()` or `adapter.get_character()` |
| `character_db.find_characters_by_name()` | `Character.objects.filter()` or `adapter.find_characters_by_name()` |
| `character_db.update_character()` | `character.save()` or `adapter.update_character()` |
| `character_db.delete_character()` | `character.delete()` or `adapter.delete_character()` |

## Usage Examples

### Running AI Workflow with Django Integration

#### From Django/Celery Task:
```python
from ai_workflow.src.django_integration import process_book_with_ai_workflow
from books.models import Book

book = Book.objects.get(book_id=book_id)
result = process_book_with_ai_workflow(
    book=book,
    clear_existing=True  # Optional: clear existing characters
)
```

#### From Command Line:
```bash
# With Django integration
python ai_workflow/src/main.py --book-id <book-uuid> --file path/to/book.txt

# Standalone mode (for testing)
python ai_workflow/src/main.py --file path/to/book.txt

# With visualization
python ai_workflow/src/main.py --visualize --book-id <book-uuid>

# Clear existing characters before processing
python ai_workflow/src/main.py --book-id <book-uuid> --clear-existing
```

### Using the Django Adapter

```python
from ai_workflow.src.databases.django_adapter import get_character_adapter

# Get adapter with book context
adapter = get_character_adapter(book_id='book-uuid-here')

# Insert a character
character_id = adapter.insert_character({
    'name': 'أحمد',
    'age': 30,
    'role': 'protagonist'
})

# Find characters by name
characters = adapter.find_characters_by_name('أحمد')

# Enhanced search with fuzzy matching
characters = adapter.find_characters_by_name_enhanced(
    'احمد',  # Will match أحمد, احمد, etc.
    similarity_threshold=0.8
)

# Update character
adapter.update_character(character_id, {
    'name': 'أحمد',
    'age': 31,
    'role': 'main protagonist'
})

# Create character relationships
adapter.create_character_relationship(
    character_id_1='char-1-uuid',
    character_id_2='char-2-uuid',
    relationship_type='friend',
    description='Best friends since childhood'
)
```

## Features Preserved

1. **Fuzzy Matching**: Arabic text normalization and fuzzy matching for character names
2. **JSON Storage**: Flexible character profiles using Django's JSONField
3. **Book Context**: Characters are properly linked to books
4. **Transaction Safety**: All operations use Django's transaction management
5. **Backward Compatibility**: The adapter provides the same interface as the old database

## Testing

Run the Django integration tests:
```bash
python manage.py test ai_workflow.tests.test_django_integration
```

Or run standalone:
```bash
python ai_workflow/tests/test_django_integration.py
```

## Migration Steps for Existing Data

If you have existing data in the old SQLite database, you can migrate it:

1. Export data from old database:
```python
from ai_workflow.src.databases.database import CharacterDatabase
old_db = CharacterDatabase()
all_characters = old_db.get_all_characters()
```

2. Import into Django models:
```python
from characters.models import Character
from books.models import Book

book = Book.objects.get(...)  # Get or create appropriate book
for char_data in all_characters:
    Character.objects.create(
        book_id=book,
        profile=char_data['profile']
    )
```

## Configuration

The Django adapter automatically initializes Django settings when imported. If you need custom settings:

```python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'your_project.settings'
```

## Troubleshooting

### Issue: Django not initialized
**Solution**: The adapter automatically sets up Django. If issues persist, ensure `DJANGO_SETTINGS_MODULE` is set.

### Issue: Characters not linked to books
**Solution**: Always provide `book_id` when creating the initial state or adapter.

### Issue: Fuzzy matching not working
**Solution**: Ensure `rapidfuzz` is installed and Arabic text normalization is working.

## Benefits of Migration

1. **Unified Database**: Single database for entire application
2. **Better Relationships**: Proper foreign keys and relationships
3. **Transaction Management**: Django's robust transaction handling
4. **Admin Interface**: Characters visible in Django admin
5. **Query Optimization**: Django's ORM query optimization
6. **Migration Support**: Django's migration system for schema changes
7. **Testing**: Better test isolation with Django's test framework

## Deprecated Components

The following components are deprecated and should not be used:
- `ai_workflow/src/databases/database.py` - Use `django_adapter.py` instead
- Direct `character_db` instance - Use `get_character_adapter()` instead
- `CharacterDatabase` class - Use `DjangoCharacterAdapter` instead

## Future Improvements

1. Add caching for frequently accessed characters
2. Implement batch operations for better performance
3. Add character versioning/history tracking
4. Enhance relationship analysis with graph algorithms
5. Add character similarity scoring across books
