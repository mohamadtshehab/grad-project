from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from faker import Faker
import random

from user.models import User
from books.models import Book
from chunks.models import Chunk
from characters.models import Character, ChunkCharacter, CharacterRelationship

fake = Faker(['en_US', 'ar_SA'])


class Command(BaseCommand):
    help = 'Seed the database with test data for API testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--books',
            type=int,
            default=8,
            help='Number of books to create (default: 8)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_database()

        users_count = options['users']
        books_count = options['books']

        self.stdout.write(
            self.style.SUCCESS(f'🌱 Starting database seeding...')
        )

        users = self.create_users(users_count)
        books = self.create_books(books_count, users)
        chunks = self.create_chunks(books)
        characters = self.create_characters(books)
        self.create_chunk_characters(chunks, characters)
        self.create_character_relationships(characters)

        self.print_summary()

    def clear_database(self):
        """Clear all existing data"""
        self.stdout.write("🗑️  Clearing existing data...")
        CharacterRelationship.objects.all().delete()
        ChunkCharacter.objects.all().delete()
        Character.objects.all().delete()
        Chunk.objects.all().delete()
        Book.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        self.stdout.write(self.style.SUCCESS("✅ Database cleared!"))

    def create_users(self, count):
        """Create test users"""
        self.stdout.write(f"👥 Creating {count} users...")
        
        users = []
        for i in range(count):
            user = User.objects.create_user(
                email=fake.email(),
                name=fake.name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='testpass123',
                is_active=True
            )
            users.append(user)
            
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(users)} users!"))
        return users

    def create_books(self, count, users):
        """Create test books"""
        self.stdout.write(f"📚 Creating {count} books...")
        
        arabic_text_samples = [
            "في يوم من الأيام، كان هناك رجل يدعى أحمد يعيش في قرية صغيرة. كان أحمد رجلاً طيب القلب، يحب مساعدة الآخرين.",
            "التقت فاطمة بصديقتها مريم في السوق. كانت فاطمة تبحث عن هدية لابنتها الصغيرة سارة.",
            "كان علي طالباً مجتهداً في الجامعة. يدرس الأدب العربي ويحلم بأن يصبح كاتباً مشهوراً يوماً ما.",
            "عاش محمد مع جده الحكيم في بيت قديم بجانب النهر. كان الجد يحكي لمحمد قصصاً رائعة عن الماضي.",
            "في المدينة الكبيرة، كانت هناك امرأة تدعى خديجة تعمل طبيبة. كانت خديجة معروفة بطيبتها ومساعدتها للفقراء."
        ]
        
        book_titles = [
            "اللص والكلاب", "الطريق", "بين القصرين", "قصر الشوق", "السكرية",
            "أولاد حارتنا", "الحرافيش", "ملحمة الحرافيش"
        ]
        
        authors = [
            "نجيب محفوظ", "يوسف إدريس", "إحسان عبد القدوس", "توفيق الحكيم"
        ]
        
        books = []
        for i in range(count):
            book_content = "\n\n".join(random.choices(arabic_text_samples, k=10))
            file_content = ContentFile(book_content.encode('utf-8'))
            
            title = book_titles[i] if i < len(book_titles) else fake.sentence(nb_words=3)
            filename = f"book_{i+1}.txt"
            
            book = Book.objects.create(
                title=title,
                author=random.choice(authors),
                description=fake.text(max_nb_chars=200),
                user_id=random.choice(users)
            )
            
            book.file.save(filename, file_content, save=True)
            books.append(book)
            
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(books)} books!"))
        return books

    def create_chunks(self, books):
        """Create text chunks for each book"""
        self.stdout.write("📄 Creating text chunks...")
        
        arabic_text_samples = [
            "في يوم من الأيام، كان هناك رجل يدعى أحمد يعيش في قرية صغيرة.",
            "التقت فاطمة بصديقتها مريم في السوق.",
            "كان علي طالباً مجتهداً في الجامعة.",
            "عاش محمد مع جده الحكيم في بيت قديم بجانب النهر.",
            "في المدينة الكبيرة، كانت هناك امرأة تدعى خديجة تعمل طبيبة."
        ]
        
        chunks = []
        for book in books:
            chunk_count = random.randint(5, 10)
            
            for i in range(chunk_count):
                chunk_text = random.choice(arabic_text_samples)
                chunk_text += " " + fake.text(max_nb_chars=300)
                
                chunk = Chunk.objects.create(
                    chunk_text=chunk_text,
                    chunk_number=i + 1,
                    book_id=book,
                    start_position=i * 500,
                    end_position=(i + 1) * 500,
                    word_count=len(chunk_text.split())
                )
                chunks.append(chunk)
                
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(chunks)} chunks!"))
        return chunks

    def create_characters(self, books):
        """Create characters for books"""
        self.stdout.write("👤 Creating characters...")
        
        character_templates = [
            {
                "name": "أحمد", "age": "35", "role": "البطل",
                "physical_characteristics": ["طويل القامة", "أسمر البشرة"],
                "personality": "طيب القلب، شجاع",
                "events": ["خرج إلى الحديقة", "ساعد جاره"],
                "relationships": ["زوج فاطمة"],
                "aliases": ["أبو محمد"]
            },
            {
                "name": "فاطمة", "age": "30", "role": "الزوجة",
                "physical_characteristics": ["متوسطة الطول", "شعر أسود"],
                "personality": "حنونة، ذكية",
                "events": ["ذهبت إلى السوق"],
                "relationships": ["زوجة أحمد"],
                "aliases": ["أم سارة"]
            },
            {
                "name": "علي", "age": "22", "role": "الطالب",
                "physical_characteristics": ["نحيف", "يرتدي نظارات"],
                "personality": "مجتهد، طموح",
                "events": ["يدرس في الجامعة"],
                "relationships": ["صديق أحمد"],
                "aliases": ["الطالب المجتهد"]
            }
        ]
        
        characters = []
        for book in books:
            character_count = random.randint(3, 5)
            
            for i in range(character_count):
                template = random.choice(character_templates)
                
                character_data = {
                    "name": template["name"] + (f" {i+1}" if i > 0 else ""),
                    "age": str(random.randint(20, 60)),
                    "role": template["role"],
                    "physical_characteristics": template["physical_characteristics"][:],
                    "personality": template["personality"],
                    "events": random.choices(template["events"], k=random.randint(1, 3)),
                    "relationships": template["relationships"][:],
                    "aliases": template["aliases"][:]
                }
                
                character = Character.objects.create(
                    book_id=book,
                    character_data=character_data
                )
                characters.append(character)
                
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(characters)} characters!"))
        return characters

    def create_chunk_characters(self, chunks, characters):
        """Create chunk-character relationships"""
        self.stdout.write("🔗 Creating chunk-character relationships...")
        
        relationships_count = 0
        
        # Group characters by book
        book_characters = {}
        for character in characters:
            book_id = character.book_id.book_id
            if book_id not in book_characters:
                book_characters[book_id] = []
            book_characters[book_id].append(character)
        
        for chunk in chunks:
            book_id = chunk.book_id.book_id
            if book_id in book_characters:
                available_characters = book_characters[book_id]
                # Use sample to avoid duplicates, but ensure we don't exceed available characters
                num_characters = min(random.randint(1, 3), len(available_characters))
                if num_characters > 0:
                    mentioned_characters = random.sample(available_characters, num_characters)
                    
                    for character in mentioned_characters:
                        ChunkCharacter.objects.create(
                            chunk_id=chunk,
                            character_id=character,
                            mention_count=random.randint(1, 5),
                            position_info={
                                "positions": [random.randint(0, 100)],
                                "context": "mentioned in narrative"
                            }
                        )
                        relationships_count += 1
                    
        self.stdout.write(self.style.SUCCESS(f"✅ Created {relationships_count} chunk-character relationships!"))

    def create_character_relationships(self, characters):
        """Create character relationships"""
        self.stdout.write("💕 Creating character relationships...")
        
        relationships_count = 0
        relationship_types = ['family', 'friend', 'enemy', 'romantic', 'colleague', 'ally']
        
        # Group characters by book
        book_characters = {}
        for character in characters:
            book_id = character.book_id.book_id
            if book_id not in book_characters:
                book_characters[book_id] = []
            book_characters[book_id].append(character)
        
        for book_id, book_chars in book_characters.items():
            if len(book_chars) < 2:
                continue
                
            for i, char1 in enumerate(book_chars):
                for char2 in book_chars[i+1:]:
                    if random.random() < 0.3:  # 30% chance
                        relationship_type = random.choice(relationship_types)
                        
                        CharacterRelationship.objects.create(
                            character_id_1=char1,
                            character_id_2=char2,
                            relationship_type=relationship_type,
                            description=f"{char1.name} و {char2.name} لديهما علاقة {relationship_type}",
                            book_id=char1.book_id
                        )
                        relationships_count += 1
                        
        self.stdout.write(self.style.SUCCESS(f"✅ Created {relationships_count} character relationships!"))

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📊 DATABASE SEEDING SUMMARY"))
        self.stdout.write("="*50)
        self.stdout.write(f"👥 Users: {User.objects.count()}")
        self.stdout.write(f"📚 Books: {Book.objects.count()}")
        self.stdout.write(f"📄 Chunks: {Chunk.objects.count()}")
        self.stdout.write(f"👤 Characters: {Character.objects.count()}")
        self.stdout.write(f"🔗 Chunk-Character relationships: {ChunkCharacter.objects.count()}")
        self.stdout.write(f"💕 Character relationships: {CharacterRelationship.objects.count()}")
        self.stdout.write("="*50)
        self.stdout.write(self.style.SUCCESS("\n🎉 Database seeding completed successfully!"))
