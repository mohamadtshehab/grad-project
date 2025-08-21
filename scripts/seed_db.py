#!/usr/bin/env python
"""
Database seeding script for API testing
Creates realistic test data for all models in the system
"""

import os
import sys
import django
from django.core.files.base import ContentFile
from faker import Faker
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')
django.setup()

# Now import Django models
from user.models import User
from books.models import Book
from chunks.models import Chunk
from characters.models import Character, ChunkCharacter, CharacterRelationship

fake = Faker(['en_US', 'ar_SA'])  # English and Arabic locales

class DatabaseSeeder:
    def __init__(self):
        self.users = []
        self.books = []
        self.chunks = []
        self.characters = []
        
        # Sample Arabic text chunks for realistic book content
        self.arabic_text_samples = [
            "في يوم من الأيام، كان هناك رجل يدعى أحمد يعيش في قرية صغيرة. كان أحمد رجلاً طيب القلب، يحب مساعدة الآخرين. في صباح أحد الأيام، استيقظ أحمد مبكراً وخرج إلى الحديقة.",
            "التقت فاطمة بصديقتها مريم في السوق. كانت فاطمة تبحث عن هدية لابنتها الصغيرة سارة. مريم اقترحت عليها أن تذهب إلى المكتبة لتشتري لها كتاباً جميلاً.",
            "كان علي طالباً مجتهداً في الجامعة. يدرس الأدب العربي ويحلم بأن يصبح كاتباً مشهوراً يوماً ما. في المساء، يجلس علي في مكتبته الصغيرة ويكتب القصص والشعر.",
            "عاش محمد مع جده الحكيم في بيت قديم بجانب النهر. كان الجد يحكي لمحمد قصصاً رائعة عن الماضي، وكان محمد يستمع بشغف إلى هذه الحكايات المثيرة.",
            "في المدينة الكبيرة، كانت هناك امرأة تدعى خديجة تعمل طبيبة. كانت خديجة معروفة بطيبتها ومساعدتها للفقراء. كل يوم، تذهب إلى العيادة وتعالج المرضى بحب وإخلاص.",
        ]
        
        # Character names and data for Arabic context
        self.character_templates = [
            {
                "name": "أحمد", "age": "35", "role": "البطل",
                "physical_characteristics": ["طويل القامة", "أسمر البشرة", "عيون بنية"],
                "personality": "طيب القلب، شجاع، مساعد للآخرين",
                "events": ["خرج إلى الحديقة", "ساعد جاره المريض", "وجد كنزاً مدفوناً"],
                "relationships": ["زوج فاطمة", "صديق علي"],
                "aliases": ["أبو محمد", "الرجل الطيب"]
            },
            {
                "name": "فاطمة", "age": "30", "role": "الزوجة",
                "physical_characteristics": ["متوسطة الطول", "شعر أسود", "عيون خضراء"],
                "personality": "حنونة، ذكية، مهتمة بالأطفال",
                "events": ["ذهبت إلى السوق", "التقت بمريم", "اشترت هدية لابنتها"],
                "relationships": ["زوجة أحمد", "صديقة مريم", "أم سارة"],
                "aliases": ["أم سارة", "الأم الحنونة"]
            },
            {
                "name": "علي", "age": "22", "role": "الطالب",
                "physical_characteristics": ["نحيف", "طويل", "يرتدي نظارات"],
                "personality": "مجتهد، طموح، محب للأدب",
                "events": ["يدرس في الجامعة", "يكتب القصص", "يحلم بأن يصبح كاتباً"],
                "relationships": ["صديق أحمد", "طالب عند الأستاذ محمود"],
                "aliases": ["الطالب المجتهد", "الكاتب الشاب"]
            },
            {
                "name": "مريم", "age": "28", "role": "الصديقة",
                "physical_characteristics": ["قصيرة القامة", "شعر بني", "ابتسامة جميلة"],
                "personality": "مرحة، نشيطة، محبة للتسوق",
                "events": ["التقت بفاطمة", "نصحتها بشراء كتاب", "ذهبت معها إلى المكتبة"],
                "relationships": ["صديقة فاطمة", "جارة خديجة"],
                "aliases": ["المرأة المرحة", "الصديقة الوفية"]
            },
            {
                "name": "خديجة", "age": "40", "role": "الطبيبة",
                "physical_characteristics": ["أنيقة المظهر", "شعر قصير", "عيون ذكية"],
                "personality": "حكيمة، طيبة، مخلصة في عملها",
                "events": ["تعالج المرضى", "تساعد الفقراء", "تعمل في العيادة"],
                "relationships": ["جارة مريم", "طبيبة العائلة"],
                "aliases": ["الطبيبة الطيبة", "الحكيمة"]
            }
        ]

    def clear_database(self):
        """Clear all existing data"""
        print("🗑️  Clearing existing data...")
        CharacterRelationship.objects.all().delete()
        ChunkCharacter.objects.all().delete()
        Character.objects.all().delete()
        Chunk.objects.all().delete()
        Book.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()  # Keep superuser
        print("✅ Database cleared!")

    def create_users(self, count=10):
        """Create test users"""
        print(f"👥 Creating {count} users...")
        for i in range(count):
            user = User.objects.create_user(
                email=fake.email(),
                name=fake.name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='testpass123',
                is_active=True
            )
            self.users.append(user)
        print(f"✅ Created {len(self.users)} users!")

    def create_books(self, count=8):
        """Create test books"""
        print(f"📚 Creating {count} books...")
        book_titles = [
            "الطريق", "بين القصرين", "قصر الشوق", "السكرية", "أولاد حارتنا", 
            "الحرافيش", "ملحمة الحرافيش", "الكرنك", "المرايا", "حديث الصباح والمساء"
        ]
        authors = ["نجيب محفوظ", "يوسف إدريس", "إحسان عبد القدوس", "توفيق الحكيم", "طه حسين"]
        
        for i in range(count):
            book_content = "\n\n".join(random.choices(self.arabic_text_samples, k=10))
            file_content = ContentFile(book_content.encode('utf-8'))
            title = book_titles[i] if i < len(book_titles) else fake.sentence(nb_words=3)
            filename = f"book_{i+1}.epub"
            
            book = Book.objects.create(
                title=title,
                author=random.choice(authors),
                description=fake.text(max_nb_chars=200),
                user=random.choice(self.users)
            )
            book.file.save(filename, file_content, save=True)
            self.books.append(book)
        print(f"✅ Created {len(self.books)} books!")

    def create_chunks(self):
        """Create text chunks for each book"""
        print("📄 Creating text chunks...")
        for book in self.books:
            chunk_count = random.randint(5, 10)
            for i in range(chunk_count):
                chunk_text = random.choice(self.arabic_text_samples)
                chunk = Chunk.objects.create(
                    chunk_text=chunk_text,
                    chunk_number=i + 1,
                    book=book,
                    word_count=len(chunk_text.split())
                )
                self.chunks.append(chunk)
        print(f"✅ Created {len(self.chunks)} chunks!")

    def create_characters(self):
        """Create characters for books"""
        print("👤 Creating characters...")
        for book in self.books:
            character_count = random.randint(3, 5)
            for i in range(character_count):
                template = random.choice(self.character_templates)
                character_data = {
                    "name": template["name"] + (f" {i+1}" if i > 0 else ""),
                    "age": str(random.randint(20, 60)),
                    "role": template["role"],
                    "personality": template["personality"],
                }
                character = Character.objects.create(
                    book=book,
                    character_data=character_data
                )
                self.characters.append(character)
        print(f"✅ Created {len(self.characters)} characters!")

    def create_chunk_characters(self):
        """Create chunk-character relationships"""
        print("🔗 Creating chunk-character relationships...")
        relationships_count = 0
        for book in self.books:
            book_chunks = list(book.chunks.all())
            book_characters = list(book.characters.all())
            if not book_characters:
                continue
            for chunk in book_chunks:
                num_mentions = random.randint(1, min(3, len(book_characters)))
                mentioned_characters = random.sample(book_characters, k=num_mentions)
                for character in mentioned_characters:
                    ChunkCharacter.objects.create(
                        chunk=chunk,
                        character=character,
                        mention_count=random.randint(1, 5)
                    )
                    relationships_count += 1
        print(f"✅ Created {relationships_count} chunk-character relationships!")

    def create_character_relationships(self):
        """Create character relationships"""
        print("💕 Creating character relationships...")
        relationships_count = 0
        relationship_types = ['family', 'friend', 'enemy', 'romantic', 'colleague']
        
        for book in self.books:
            book_characters = list(book.characters.all())
            if len(book_characters) < 2:
                continue
            
            for i, char1 in enumerate(book_characters):
                for char2 in book_characters[i+1:]:
                    if random.random() < 0.5:
                        
                        # --- FIX STARTS HERE ---
                        # Enforce canonical order (pk of 'from' must be less than pk of 'to').
                        # We compare the string representation of the UUIDs.
                        if str(char1.pk) > str(char2.pk):
                            from_char, to_char = char2, char1
                        else:
                            from_char, to_char = char1, char2
                        # --- FIX ENDS HERE ---

                        relationship_type = random.choice(relationship_types)
                        
                        CharacterRelationship.objects.create(
                            from_character=from_char, # Use the sorted variable
                            to_character=to_char,   # Use the sorted variable
                            relationship_type=relationship_type,
                            description=f"{from_char.name} و {to_char.name} لديهما علاقة {relationship_type}",
                            book=book
                        )
                        relationships_count += 1
        print(f"✅ Created {relationships_count} character relationships!")
    
    def print_summary(self):
        """Print summary of created data"""
        print("\n" + "="*50)
        print("📊 DATABASE SEEDING SUMMARY")
        print("="*50)
        print(f"👥 Users: {User.objects.count()}")
        print(f"📚 Books: {Book.objects.count()}")
        print(f"📄 Chunks: {Chunk.objects.count()}")
        print(f"👤 Characters: {Character.objects.count()}")
        print(f"🔗 Chunk-Character relationships: {ChunkCharacter.objects.count()}")
        print(f"💕 Character relationships: {CharacterRelationship.objects.count()}")
        print("="*50)
        
        sample_book = Book.objects.first()
        if sample_book:
            print(f"\n📋 Sample Book: {sample_book.title} by {sample_book.author}")
        
        sample_character = Character.objects.first()
        if sample_character:
            print(f"📋 Sample Character: {sample_character.name} - {sample_character.character_data.get('role', 'Unknown')}")
        
        print("\n🎉 Database seeding completed successfully!")

    def seed_all(self):
        """Run the complete seeding process"""
        print("🌱 Starting database seeding...")
        print("="*50)
        self.clear_database()
        self.create_users()
        self.create_books()
        self.create_chunks()
        self.create_characters()
        self.create_chunk_characters()
        self.create_character_relationships()
        self.print_summary()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.seed_all()