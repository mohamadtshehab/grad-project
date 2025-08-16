#!/usr/bin/env python
"""
EPUB Books Addition Script
Adds EPUB books from ai_workflow/resources to the database
"""

import os
import sys
import django
from django.core.files import File
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')
django.setup()

# Now import Django models
from user.models import User
from books.models import Book

class EPUBBookAdder:
    def __init__(self):
        self.added_books = []
        
    def get_random_user(self):
        """Get a random user from the database, or create one if none exist"""
        users = User.objects.all()
        if users.exists():
            return random.choice(users)
        else:
            # Create a default user if none exist
            user = User.objects.create_user(
                email='admin@example.com',
                name='Admin User',
                first_name='Admin',
                last_name='User',
                password='admin123',
                is_active=True
            )
            print(f"📝 Created default user: {user.email}")
            return user
    
    def add_epub_books(self):
        """Add EPUB books from ai_workflow/resources to the database"""
        print("📖 Adding EPUB books from resources...")
        print("="*50)
        
        # Define the EPUB books from resources
        epub_books = [
            {
                "source_path": "ai_workflow/resources/texts/اللص والكلاب.epub",
                "title": "اللص والكلاب",
                "author": "نجيب محفوظ",
                "description": "رواية من أشهر أعمال نجيب محفوظ، تحكي قصة سعيد مهران بعد خروجه من السجن وبحثه عن الانتقام من الذين خانوه. تعتبر من الروايات الواقعية التي تصور المجتمع المصري في فترة الخمسينيات."
            },
            {
                "source_path": "ai_workflow/resources/texts/01- رواية أرض الإله - احمد مراد_djvu.epub",
                "title": "أرض الإله",
                "author": "أحمد مراد",
                "description": "رواية تاريخية مشوقة تدور أحداثها في مصر القديمة، وتحكي قصة الصراع بين الخير والشر في عالم الفراعنة. تجمع الرواية بين التاريخ والخيال في إطار درامي مثير."
            }
        ]
        
        # Get a random user to assign books to
        user = self.get_random_user()
        
        for epub_info in epub_books:
            source_path = epub_info["source_path"]
            
            # Check if source file exists
            if not os.path.exists(source_path):
                print(f"⚠️  EPUB file not found: {source_path}")
                continue
            
            # Check if book already exists
            existing_book = Book.objects.filter(title=epub_info["title"]).first()
            if existing_book:
                print(f"📚 Book '{epub_info['title']}' already exists (ID: {existing_book.book_id})")
                print(f"    File: {existing_book.file.name}")
                self.added_books.append(existing_book)
                continue
                
            try:
                # Create book entry
                book = Book.objects.create(
                    title=epub_info["title"],
                    author=epub_info["author"],
                    description=epub_info["description"],
                    user_id=user
                )
                
                # Copy EPUB file to media directory
                with open(source_path, 'rb') as epub_file:
                    django_file = File(epub_file)
                    filename = f"{epub_info['title'].replace(' ', '_').replace('/', '_')}.epub"
                    book.file.save(filename, django_file, save=True)
                
                self.added_books.append(book)
                print(f"✅ Added EPUB: {epub_info['title']}")
                print(f"    Author: {epub_info['author']}")
                print(f"    File: {book.file.name}")
                print(f"    Book ID: {book.book_id}")
                print(f"    User: {user.name} ({user.email})")
                print()
                
            except Exception as e:
                print(f"❌ Error creating book '{epub_info['title']}': {str(e)}")
                continue
        
        return self.added_books
    
    def print_summary(self):
        """Print summary of added books"""
        print("\n" + "="*50)
        print("📊 EPUB BOOKS ADDITION SUMMARY")
        print("="*50)
        
        total_books = Book.objects.count()
        epub_books = Book.objects.filter(file__endswith='.epub')
        
        print(f"📚 Total Books in Database: {total_books}")
        print(f"📖 Total EPUB Books: {epub_books.count()}")
        print(f"➕ Books Added This Session: {len(self.added_books)}")
        
        if epub_books.exists():
            print(f"\n📖 All EPUB Books in Database:")
            print("-" * 40)
            for book in epub_books:
                print(f"   • {book.title} by {book.author}")
                print(f"     File: {book.file.name}")
                print(f"     ID: {book.book_id}")
                print(f"     User: {book.user_id.name}")
                print()
        
        if self.added_books:
            print("🎯 Ready for AI Workflow Processing:")
            print("-" * 40)
            for book in self.added_books:
                print(f"   Book ID: {book.book_id}")
                print(f"   Title: {book.title}")
                print(f"   File Path: {book.file.path}")
                print()
        
        print("🎉 EPUB books addition completed successfully!")
        
        if self.added_books:
            print("\n💡 Usage Tips:")
            print("- Use the Book IDs above when testing the AI workflow")
            print("- The files are now stored in the media/books/ directory")
            print("- You can process these books through the character extraction pipeline")

def main():
    """Main function to run the EPUB book addition process"""
    print("🌱 Starting EPUB Books Addition...")
    
    adder = EPUBBookAdder()
    added_books = adder.add_epub_books()
    adder.print_summary()
    
    if added_books:
        print(f"\n✨ Successfully processed {len(added_books)} EPUB books!")
    else:
        print("\n📝 No new EPUB books were added (they may already exist)")

if __name__ == "__main__":
    main()
