from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
from books.models import Book
from user.models import User
import os
import uuid
from pathlib import Path
import ebooklib
from ebooklib import epub


def epub_to_raw_html_string(epub_path):
    """
    Opens an EPUB and concatenates the raw, unparsed HTML/XHTML source
    code of its content documents into a single string.
    """
    book = epub.read_epub(epub_path)
    html_parts = []

    # Find all the content documents (the chapters)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        # Get the raw byte content
        content_bytes = item.get_content()
        # Decode it into a string, KEEPING ALL TAGS
        content_string = content_bytes.decode('utf-8', errors='ignore')
        html_parts.append(content_string)
    
    # Join the raw HTML of each chapter with a separator
    return "\n\n\n\n".join(html_parts)


class Command(BaseCommand):
    help = 'Add books from ai_workflow/resources/texts/test_set to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email of the user to assign books to (will create if not exists)',
            default='test@example.com'
        )
        parser.add_argument(
            '--user-name',
            type=str,
            help='Name of the user to assign books to',
            default='Test User'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-upload even if book already exists'
        )
        parser.add_argument(
            '--add-txt',
            action='store_true',
            help='Add TXT files to existing books that don\'t have them'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to add test books to database...'))
        
        # Get or create user
        user = self._get_or_create_user(options['user_email'], options['user_name'], options)
        
        # Get test set directory
        test_set_dir = Path('ai_workflow/resources/texts/test_set')
        if not test_set_dir.exists():
            raise CommandError(f'Test set directory not found: {test_set_dir}')
        
        # Find all EPUB files
        epub_files = list(test_set_dir.glob('*.epub'))
        if not epub_files:
            raise CommandError(f'No EPUB files found in {test_set_dir}')
        
        self.stdout.write(f'Found {len(epub_files)} EPUB files in test set directory')
        
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        for epub_file in epub_files:
            try:
                result = self._process_epub_file(epub_file, user, options)
                if result == 'added':
                    added_count += 1
                elif result == 'skipped':
                    skipped_count += 1
                elif result == 'error':
                    error_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {epub_file.name}: {str(e)}')
                )
                error_count += 1
        
        # Handle adding TXT files to existing books if requested
        if options.get('add_txt') and not options.get('dry_run'):
            self.stdout.write('\n' + '='*50)
            self.stdout.write('Adding TXT files to existing books...')
            txt_added_count = 0
            txt_error_count = 0
            
            for epub_file in epub_files:
                title = self._extract_title_from_filename(epub_file.name)
                existing_book = Book.objects.filter(title=title).first()
                
                if existing_book and not existing_book.txt_file:
                    try:
                        result = self._add_txt_to_existing_book(existing_book, epub_file)
                        if result == 'added':
                            txt_added_count += 1
                        elif result == 'error':
                            txt_error_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error adding TXT to "{title}": {str(e)}')
                        )
                        txt_error_count += 1
            
            if txt_added_count > 0 or txt_error_count > 0:
                self.stdout.write(f'  TXT files added: {txt_added_count}')
                self.stdout.write(f'  TXT errors: {txt_error_count}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(f'  Added: {added_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Errors: {error_count}')
        self.stdout.write(f'  Total processed: {len(epub_files)}')
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING('Some books had errors. Check the output above for details.')
            )
        
        self.stdout.write(self.style.SUCCESS('Test books addition completed!'))

    def _get_or_create_user(self, email, name, options):
        """Get existing user or create a new one"""
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f'Using existing user: {user.name} ({user.email})')
        except User.DoesNotExist:
            if not options.get('dry_run'):
                user = User.objects.create(
                    email=email,
                    name=name,
                    password='test123',
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created new user: {user.name} ({user.email})')
                )
            else:
                self.stdout.write(f'Would create user: {name} ({email})')
                # Create a mock user object for dry run
                user = type('MockUser', (), {'id': 'mock-id', 'name': name, 'email': email})()
        return user

    def _process_epub_file(self, epub_file, user, options):
        """Process a single EPUB file"""
        filename = epub_file.name
        title = self._extract_title_from_filename(filename)
        
        # Check if book already exists
        existing_book = Book.objects.filter(title=title).first()
        if existing_book and not options['force']:
            self.stdout.write(f'📚 Skipping "{title}" - already exists (ID: {existing_book.id})')
            return 'skipped'
        
        if options['dry_run']:
            self.stdout.write(f'📖 Would add: {title} from {filename}')
            return 'added'
        
        try:
            # Create book entry
            book = Book.objects.create(
                title=title,
                user=user,
                processing_status='pending'
            )
            
            # Copy EPUB file to media directory
            with open(epub_file, 'rb') as epub_file_obj:
                django_file = File(epub_file_obj)
                book.file.save(filename, django_file, save=True)
            
            # Convert EPUB to TXT and save
            try:
                epub_path = book.file.path
                raw_html_content = epub_to_raw_html_string(epub_path)
                txt_filename = os.path.splitext(filename)[0] + '.txt'
                
                # Save the generated TXT content to the model's txt_file field
                book.txt_file.save(
                    txt_filename,
                    ContentFile(raw_html_content.encode('utf-8')),
                    save=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Added "{title}" (ID: {book.id}) with TXT conversion')
                )
            except Exception as txt_error:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  TXT conversion failed for "{title}": {str(txt_error)}')
                )
                # Still consider it added even if TXT conversion fails
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Added "{title}" (ID: {book.id}) - EPUB only')
                )
            
            return 'added'
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to add "{title}": {str(e)}')
            )
            return 'error'

    def _add_txt_to_existing_book(self, book, epub_file):
        """Add TXT file to an existing book"""
        try:
            # Convert EPUB to TXT
            raw_html_content = epub_to_raw_html_string(epub_file)
            txt_filename = os.path.splitext(epub_file.name)[0] + '.txt'
            
            # Save the generated TXT content to the model's txt_file field
            book.txt_file.save(
                txt_filename,
                ContentFile(raw_html_content.encode('utf-8')),
                save=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'📝 Added TXT file to "{book.title}"')
            )
            return 'added'
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to add TXT to "{book.title}": {str(e)}')
            )
            return 'error'

    def _extract_title_from_filename(self, filename):
        """Extract book title from filename"""
        # Remove .epub extension
        title = filename.replace('.epub', '')
        
        # Clean up the title (remove any special characters that might cause issues)
        # This is a simple approach - could be enhanced with more sophisticated cleaning
        return title.strip()
