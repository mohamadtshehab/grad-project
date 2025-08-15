# Book ID Integration Guide

## Overview

The AI workflow now uses **book_id-based file path resolution**, eliminating the need to manually pass file paths. This simplifies the integration and makes the workflow more robust.

## Key Changes

### 1. **File Path Storage Update**
- **Old**: `books/user_{user_id}/{filename}`
- **New**: `books/book_{book_id}/{filename}`

### 2. **Automatic File Path Resolution**
The workflow now automatically resolves file paths from book IDs:

```python
# Old way - manual file path
result = process_book_with_ai_workflow(
    book=book,
    file_path="/path/to/file.epub",
    clear_existing=True
)

# New way - automatic file path resolution
result = process_book_with_ai_workflow(
    book=book,
    clear_existing=True  # file_path automatically resolved from book.file
)
```

### 3. **Command Line Interface**
```bash
# Old way
python ai_workflow/src/main.py --book-id <uuid> --file /path/to/file.epub

# New way - file path automatically resolved
python ai_workflow/src/main.py --book-id <uuid>
```

## Usage Examples

### 1. **Django Integration**
```python
from ai_workflow.src.django_integration import process_book_with_ai_workflow
from books.models import Book

# Get book by ID
book = Book.objects.get(book_id="your-book-uuid-here")

# Process book (file path automatically resolved)
result = process_book_with_ai_workflow(
    book=book,
    clear_existing=True
)

print(f"Extracted {result['total_characters']} characters")
```

### 2. **Celery Task**
```python
from books.tasks_ai_workflow import extract_characters_from_book

# Start background character extraction
extract_characters_from_book.delay(
    job_id="job-uuid",
    user_id="user-uuid", 
    book_id="book-uuid",
    clear_existing=True
)
```

### 3. **Command Line**
```bash
# Process a specific book
uv run python ai_workflow/src/main.py --book-id d66fe9d0-44fa-4787-955f-50b098cd1157

# Clear existing characters and process
uv run python ai_workflow/src/main.py --book-id d66fe9d0-44fa-4787-955f-50b098cd1157 --clear-existing

# Visualize workflow graph
uv run python ai_workflow/src/main.py --visualize
```

### 4. **API Endpoint**
```bash
# Start character extraction via API
curl -X POST http://localhost:8000/api/books/{book_id}/extract-characters/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"clear_existing": true}'
```

## Helper Methods

### Book Model Methods
```python
from books.models import Book

# Get file path from book ID
file_path = Book.get_file_path_by_id("book-uuid-here")

# Check if book has file
book = Book.objects.get(book_id="book-uuid")
if book.file:
    print(f"File: {book.file.path}")
else:
    print("No file attached")
```

### State Creation
```python
from ai_workflow.src.schemas.states import create_initial_state

# Automatic file path resolution from book_id
state = create_initial_state(book_id="book-uuid-here")
print(f"File path: {state['file_path']}")
print(f"Book ID: {state['book_id']}")

# Manual file path (fallback)
state = create_initial_state(file_path="/path/to/file.txt")
```

## Benefits

1. **Simplified API**: No need to pass file paths manually
2. **Consistency**: File paths always correctly resolved from database
3. **Error Reduction**: Eliminates file path mismatches
4. **Better Organization**: Files organized by book ID instead of user ID
5. **Easier Integration**: Just pass book_id and everything else is automatic

## Migration Notes

### For Existing Files
Existing files with the old `user_` prefix will continue to work. New uploads will use the `book_` prefix.

### For API Clients
Remove any `file_path` parameters from your API calls - they're no longer needed:

```python
# Old
response = requests.post('/api/process/', {
    'book_id': book_id,
    'file_path': '/path/to/file.epub'  # Remove this
})

# New  
response = requests.post('/api/process/', {
    'book_id': book_id  # File path auto-resolved
})
```

## Error Handling

The system gracefully handles missing files:

```python
try:
    result = process_book_with_ai_workflow(book=book)
except ValueError as e:
    if "has no file attached" in str(e):
        print("Book has no file - please upload a file first")
    elif "not found in database" in str(e):
        print("Book not found")
```

## Testing

Test the integration:
```bash
# Check available books
uv run python manage.py shell -c "
from books.models import Book
for book in Book.objects.all()[:5]:
    print(f'{book.book_id}: {book.title} - Has file: {bool(book.file)}')
"

# Test with a specific book
uv run python ai_workflow/src/main.py --book-id <your-book-id>
```

This integration makes the AI workflow much more user-friendly and robust! 🚀
