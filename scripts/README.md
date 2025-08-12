# Database Seeding and API Testing Scripts

This directory contains scripts to help you seed your database with test data and test your API endpoints.

## 📁 Files

- `seed_db.py` - Standalone database seeding script
- `test_api.py` - API testing script
- `README.md` - This file

## 🌱 Database Seeding

### Method 1: Django Management Command (Recommended)

```bash
# Basic seeding with default values
python manage.py seed_db

# Seed with custom parameters
python manage.py seed_db --users 15 --books 10

# Clear existing data and seed fresh
python manage.py seed_db --clear --users 20 --books 12
```

### Method 2: Standalone Script

```bash
# Run from project root
cd /path/to/your/project
python scripts/seed_db.py
```

## 🧪 API Testing

### Prerequisites

1. Install required packages:
```bash
pip install requests faker
```

2. Make sure your Django server is running:
```bash
python manage.py runserver
```

3. Run the seeding script first to populate data

### Running the Tests

```bash
# Run comprehensive API tests
python scripts/test_api.py
```

The script will test:
- User registration and authentication
- Books CRUD operations
- Chunks listing
- Characters management
- Character relationships
- File uploads
- AI workflow endpoints (if available)

## 📊 Generated Test Data

The seeding script creates:

### Users (10 by default)
- Random names and emails
- Password: `testpass123` for all test users
- Active accounts ready for API testing

### Books (8 by default)
- Arabic book titles (classic literature)
- Famous Arabic authors
- Sample Arabic text content
- Associated with random users

### Text Chunks (5-10 per book)
- Realistic Arabic text samples
- Sequential numbering
- Position and word count metadata

### Characters (3-5 per book)
- Arabic names (أحمد، فاطمة، علي، مريم، خديجة)
- Detailed character profiles:
  - Age, role, physical characteristics
  - Personality traits
  - Events and relationships
  - Aliases
- JSON data structure matching your AI workflow

### Chunk-Character Relationships
- Links characters to specific text chunks
- Mention counts and position information
- Realistic distribution across chunks

### Character Relationships
- Family, friend, romantic, and other relationship types
- Bi-directional relationships between characters
- Book-specific relationship contexts

## 🎯 Sample API Endpoints to Test

Based on your models, you might want to create these endpoints:

```
GET    /api/users/                     # List users
GET    /api/books/                     # List books
POST   /api/books/                     # Create book
GET    /api/books/{id}/                # Book detail
PUT    /api/books/{id}/                # Update book
DELETE /api/books/{id}/                # Delete book
POST   /api/books/upload/              # Upload book file

GET    /api/books/{id}/chunks/         # List chunks for book
GET    /api/chunks/{id}/               # Chunk detail

GET    /api/books/{id}/characters/     # List characters for book
GET    /api/characters/{id}/           # Character detail
PUT    /api/characters/{id}/           # Update character
DELETE /api/characters/{id}/           # Delete character

GET    /api/books/{id}/relationships/  # Character relationships for book
POST   /api/relationships/             # Create relationship
DELETE /api/relationships/{id}/        # Delete relationship

# AI Workflow Endpoints
POST   /api/ai/process-book/           # Process book with AI
POST   /api/ai/extract-characters/     # Extract characters from text
POST   /api/ai/analyze-relationships/  # Analyze character relationships
GET    /api/ai/processing-status/{id}/ # Check processing status
```

## 🔧 Customization

### Modifying Test Data

Edit the arrays in the seeding scripts to customize:
- Character names and profiles
- Book titles and authors
- Text samples
- Relationship types

### Adding More Test Scenarios

In `test_api.py`, you can add more test methods:

```python
def test_custom_endpoint(self):
    """Test your custom endpoint"""
    response = self.session.get(f"{self.base_url}/api/your-endpoint/")
    # Add your assertions here
```

### Environment Configuration

You can modify the base URL in `test_api.py`:

```python
# For different environments
tester = APITester(base_url='http://localhost:8000')     # Development
tester = APITester(base_url='https://your-api.com')      # Production
```

## 📋 Sample Output

### Seeding Output
```
🌱 Starting database seeding...
==================================================
🗑️  Clearing existing data...
✅ Database cleared!
👥 Creating 10 users...
✅ Created 10 users!
📚 Creating 8 books...
✅ Created 8 books!
📄 Creating text chunks...
✅ Created 67 chunks!
👤 Creating characters...
✅ Created 31 characters!
🔗 Creating chunk-character relationships...
✅ Created 89 chunk-character relationships!
💕 Creating character relationships...
✅ Created 23 character relationships!

📊 DATABASE SEEDING SUMMARY
==================================================
👥 Users: 10
📚 Books: 8
📄 Chunks: 67
👤 Characters: 31
🔗 Chunk-Character relationships: 89
💕 Character relationships: 23
==================================================
🎉 Database seeding completed successfully!
```

### API Testing Output
```
🧪 API Testing Script
==================================================
[14:30:15] INFO: Testing user registration...
[14:30:15] SUCCESS: ✅ User registration successful
[14:30:16] INFO: Testing books list...
[14:30:16] SUCCESS: ✅ Retrieved 8 books
[14:30:16] INFO: Testing book detail for ID: abc123...
[14:30:16] SUCCESS: ✅ Retrieved book: اللص والكلاب
🎉 API testing completed!
```

## 🚨 Important Notes

1. **Database Backup**: The `--clear` option will delete all existing data except superusers
2. **File Uploads**: Test files are created in memory and saved to your media directory
3. **Authentication**: The API tester handles token-based authentication automatically
4. **Arabic Text**: All text samples use proper Arabic encoding (UTF-8)
5. **Realistic Data**: Character profiles follow Arabic naming conventions and cultural context

## 🤝 Contributing

To add more test data or scenarios:

1. Add new templates to the `character_templates` array
2. Include more Arabic text samples in `arabic_text_samples`
3. Extend the API testing methods in `test_api.py`
4. Update this README with new features
