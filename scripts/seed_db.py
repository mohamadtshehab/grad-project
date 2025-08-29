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
                "name": "أحمد", "role": "البطل",
                "physical_characteristics": ["طويل القامة", "أسمر البشرة", "عيون بنية"],
                "personality": "طيب القلب، شجاع، مساعد للآخرين",
                "events": ["خرج إلى الحديقة", "ساعد جاره المريض", "وجد كنزاً مدفوناً"],
                "relationships": ["زوج فاطمة", "صديق علي"],
                "aliases": ["أبو محمد", "الرجل الطيب"]
            },
            {
                "name": "فاطمة", "role": "الزوجة",
                "physical_characteristics": ["متوسطة الطول", "شعر أسود", "عيون خضراء"],
                "personality": "حنونة، ذكية، مهتمة بالأطفال",
                "events": ["ذهبت إلى السوق", "التقت بمريم", "اشترت هدية لابنتها"],
                "relationships": ["زوجة أحمد", "صديقة مريم", "أم سارة"],
                "aliases": ["أم سارة", "الأم الحنونة"]
            },
            {
                "name": "علي", "role": "الطالب",
                "physical_characteristics": ["نحيف", "طويل", "يرتدي نظارات"],
                "personality": "مجتهد، طموح، محب للأدب",
                "events": ["يدرس في الجامعة", "يكتب القصص", "يحلم بأن يصبح كاتباً"],
                "relationships": ["صديق أحمد", "طالب عند الأستاذ محمود"],
                "aliases": ["الطالب المجتهد", "الكاتب الشاب"]
            },
            {
                "name": "مريم", "role": "الصديقة",
                "physical_characteristics": ["قصيرة القامة", "شعر بني", "ابتسامة جميلة"],
                "personality": "مرحة، نشيطة، محبة للتسوق",
                "events": ["التقت بفاطمة", "نصحتها بشراء كتاب", "ذهبت معها إلى المكتبة"],
                "relationships": ["صديقة فاطمة", "جارة خديجة"],
                "aliases": ["المرأة المرحة", "الصديقة الوفية"]
            },
            {
                "name": "خديجة", "role": "الطبيبة",
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
            "الطريق", "بين القصرين", "قصر الشوق", "السكرية",
            "أولاد حارتنا", "الحرافيش", "ملحمة الحرافيش", "الكرنك", "المرايا",
            "حديث الصباح والمساء", "أصداء السيرة الذاتية", "الباقي من الزمن ساعة",
            "رحلة ابن فطومة", "ليالي ألف ليلة"
        ]
        authors = ["نجيب محفوظ", "يوسف إدريس", "إحسان عبد القدوس", "توفيق الحكيم", "طه حسين"]
        
        for i in range(count):
            book_content = "\n\n".join(random.choices(self.arabic_text_samples, k=10))
            file_content = ContentFile(book_content.encode('utf-8'))
            title = book_titles[i] if i < len(book_titles) else fake.sentence(nb_words=3)
            filename = f"book_{i+1}.epub"
            
            book = Book.objects.create(
                title=title,
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
                # Create character without profile (profiles are now chunk-based)
                character = Character.objects.create(
                    book=book
                )
                self.characters.append(character)
        print(f"✅ Created {len(self.characters)} characters!")

    def create_chunk_characters(self):
        """Create chunk-character relationships with character profiles"""
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
                    # Create character profile for this chunk
                    template = random.choice(self.character_templates)
                    profile = {
                        "name": template["name"] + (f" {str(character.id)[:8]}" if character.id else ""),
                        "role": template["role"],
                        "personality": template["personality"],
                        "events": template["events"],
                        "relations": template["relationships"],
                        "aliases": template["aliases"],
                        "physical_characteristics": template["physical_characteristics"]
                    }
                    ChunkCharacter.objects.create(
                        chunk=chunk,
                        character=character,
                        character_profile=profile
                    )
                    relationships_count += 1
        print(f"✅ Created {len(self.characters)} chunk-character relationships!")

    def create_character_relationships(self):
        """Create character relationships"""
        print("💕 Creating character relationships...")
        relationships_count = 0
        relationship_types = ['family', 'friend', 'enemy', 'romantic', 'colleague']
        
        for book in self.books:
            book_characters = list(book.characters.all())
            book_chunks = list(book.chunks.all())
            if len(book_characters) < 2 or not book_chunks:
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
                        
                        # Create relationship in a random chunk of the book
                        chunk = random.choice(book_chunks)
                        
                        CharacterRelationship.objects.create(
                            from_character=from_char,
                            to_character=to_char,
                            relationship_type=relationship_type,
                            chunk=chunk
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
            print(f"\n📋 Sample Book: {sample_book.title}")
        
        sample_character = Character.objects.first()
        if sample_character:
            # Get character name from latest chunk profile
            chunk_char = ChunkCharacter.objects.filter(character=sample_character).first()
            if chunk_char and chunk_char.character_profile:
                char_name = chunk_char.character_profile.get('name', 'Unknown')
                char_role = chunk_char.character_profile.get('role', 'Unknown')
                print(f"📋 Sample Character: {char_name} - {char_role}")
            else:
                print(f"📋 Sample Character: {sample_character.id} - No profile yet")
        
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