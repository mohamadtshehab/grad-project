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
from ai_workflow.src.preprocessors.epub.txt_to_epub_converter import convert_txt_to_epub

class EPUBBookAdder:
    def __init__(self, default_only=False):
        self.added_books = []
        self.default_only = default_only
        
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
        """Add books from ai_workflow/resources to the database.

        - If EPUB files exist, import them directly.
        - If only TXT files exist, convert to EPUB and also save TXT to `Book.txt_file`.
        """
        if self.default_only:
            print("📖 Adding default books: أرض الإله & اللص والكلاب...")
        else:
            print("📖 Adding books from resources (EPUB or TXT → EPUB)...")
        print("="*50)

        if self.default_only:
            # Only add the two default books
            default_books = [
                {
                    "title": "أرض الإله",
                    "author": "أحمد مراد",
                    "description": "رواية تاريخية مشوقة تدور أحداثها في مصر القديمة، وتحكي قصة الصراع بين الخير والشر في عالم الفراعنة. تجمع الرواية بين التاريخ والخيال في إطار درامي مثير.",
                    "search_patterns": ["أرض الإله", "ارض الاله", "01- رواية أرض الإله", "احمد مراد"]
                },
                {
                    "title": "اللص والكلاب",
                    "author": "نجيب محفوظ", 
                    "description": "رواية من أشهر أعمال نجيب محفوظ، تحكي قصة سعيد مهران بعد خروجه من السجن وبحثه عن الانتقام من الذين خانوه. تعتبر من الروايات الواقعية التي تصور المجتمع المصري في فترة الخمسينيات.",
                    "search_patterns": ["اللص والكلاب", "نجيب محفوظ"]
                }
            ]
            return self._add_default_books(default_books)

        resources_dir = os.path.join('ai_workflow', 'resources', 'texts')
        if not os.path.isdir(resources_dir):
            print(f"⚠️  Resources directory not found: {resources_dir}")
            return self.added_books

        # Collect files
        epubs = []
        txts = []
        for fname in os.listdir(resources_dir):
            lower = fname.lower()
            full_path = os.path.join(resources_dir, fname)
            if not os.path.isfile(full_path):
                continue
            if lower.endswith('.epub'):
                epubs.append(full_path)
            elif lower.endswith('.txt'):
                txts.append(full_path)

        # Prefer importing existing EPUBs
        files_to_process = [(p, 'epub') for p in epubs] + [(p, 'txt') for p in txts]

        if not files_to_process:
            print("⚠️  No EPUB or TXT files found in resources.")
            return self.added_books

        # Get a random user to assign books to
        user = self.get_random_user()

        for path, kind in files_to_process:
            base = os.path.basename(path)
            name_no_ext = os.path.splitext(base)[0]
            title = name_no_ext.replace('_', ' ').strip()

            # Skip if book with same title exists
            existing_book = Book.objects.filter(title=title).first()
            if existing_book:
                print(f"📚 Book '{title}' already exists (ID: {existing_book.book_id})")
                print(f"    File: {existing_book.file.name}")
                self.added_books.append(existing_book)
                continue

            try:
                # Create book entry
                book = Book.objects.create(
                    title=title,
                    author=None,
                    description=None,
                    user_id=user
                )

                # If TXT, convert to EPUB and optionally save TXT to model
                if kind == 'txt':
                    print(f"🛠️  Converting TXT to EPUB: {base}")
                    generated_epub = convert_txt_to_epub(
                        path,
                        title=title,
                        author="Unknown",
                        language='ar',
                        output_dir=None,
                    )
                    # Save TXT to book.txt_file as well
                    with open(path, 'rb') as txt_fp:
                        book.txt_file.save(f"{name_no_ext}.txt", File(txt_fp), save=True)
                    source_epub_path = generated_epub
                else:
                    source_epub_path = path

                # Save EPUB to book.file
                with open(source_epub_path, 'rb') as epub_file:
                    django_file = File(epub_file)
                    safe_filename = f"{name_no_ext}.epub".replace('/', '_')
                    book.file.save(safe_filename, django_file, save=True)

                self.added_books.append(book)
                print(f"✅ Added Book: {title}")
                print(f"    File: {book.file.name}")
                if book.txt_file:
                    print(f"    TXT:  {book.txt_file.name}")
                print(f"    Book ID: {book.book_id}")
                print(f"    User: {user.name} ({user.email})")
                print()

            except Exception as e:
                print(f"❌ Error creating book '{title}': {str(e)}")
                continue

        return self.added_books
    
    def _add_default_books(self, default_books):
        """Add the two default books by searching for them in resources"""
        resources_dir = os.path.join('ai_workflow', 'resources', 'texts')
        if not os.path.isdir(resources_dir):
            print(f"⚠️  Resources directory not found: {resources_dir}")
            return self.added_books

        user = self.get_random_user()

        for book_info in default_books:
            title = book_info["title"]
            author = book_info["author"]
            description = book_info["description"]
            search_patterns = book_info["search_patterns"]

            # Check if book already exists
            existing_book = Book.objects.filter(title=title).first()
            if existing_book:
                print(f"📚 Book '{title}' already exists (ID: {existing_book.book_id})")
                print(f"    File: {existing_book.file.name}")
                self.added_books.append(existing_book)
                continue

            # Search for matching files
            found_file = None
            for fname in os.listdir(resources_dir):
                full_path = os.path.join(resources_dir, fname)
                if not os.path.isfile(full_path):
                    continue
                
                # Check if filename matches any search pattern
                for pattern in search_patterns:
                    if pattern.lower() in fname.lower():
                        found_file = (full_path, 'epub' if fname.lower().endswith('.epub') else 'txt')
                        break
                if found_file:
                    break

            if not found_file:
                print(f"⚠️  No file found for '{title}' with patterns: {search_patterns}")
                continue

            path, kind = found_file
            try:
                # Create book entry with metadata
                book = Book.objects.create(
                    title=title,
                    author=author,
                    description=description,
                    user_id=user
                )

                # Handle file conversion and saving
                if kind == 'txt':
                    print(f"🛠️  Converting TXT to EPUB: {os.path.basename(path)}")
                    generated_epub = convert_txt_to_epub(
                        path,
                        title=title,
                        author=author,
                        language='ar',
                        output_dir=None,
                    )
                    # Save TXT to book.txt_file
                    with open(path, 'rb') as txt_fp:
                        book.txt_file.save(f"{title.replace(' ', '_')}.txt", File(txt_fp), save=True)
                    source_epub_path = generated_epub
                else:
                    source_epub_path = path

                # Save EPUB to book.file
                with open(source_epub_path, 'rb') as epub_file:
                    django_file = File(epub_file)
                    safe_filename = f"{title.replace(' ', '_')}.epub"
                    book.file.save(safe_filename, django_file, save=True)

                self.added_books.append(book)
                print(f"✅ Added Book: {title}")
                print(f"    Author: {author}")
                print(f"    File: {book.file.name}")
                if book.txt_file:
                    print(f"    TXT:  {book.txt_file.name}")
                print(f"    Book ID: {book.book_id}")
                print(f"    User: {user.name} ({user.email})")
                print()

            except Exception as e:
                print(f"❌ Error creating book '{title}': {str(e)}")
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Add EPUB books from resources to database')
    parser.add_argument(
        '--default',
        action='store_true',
        help='Only add the two default books: أرض الإله & اللص والكلاب'
    )
    args = parser.parse_args()
    
    print("🌱 Starting EPUB Books Addition...")
    
    adder = EPUBBookAdder(default_only=args.default)
    added_books = adder.add_epub_books()
    adder.print_summary()
    
    if added_books:
        print(f"\n✨ Successfully processed {len(added_books)} books!")
    else:
        print("\n📝 No new books were added (they may already exist)")

if __name__ == "__main__":
    main()
