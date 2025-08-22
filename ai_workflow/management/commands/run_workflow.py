from django.core.management.base import BaseCommand, CommandError
from books.models import Book
from ai_workflow.src.graphs.orhcestrator.graph_builders import orchestrator_graph
from ai_workflow.src.graphs.subgraphs.validator.graph_builders import validator_graph
from ai_workflow.src.graphs.subgraphs.preprocessor.graph_builders import preprocessor_graph
from ai_workflow.src.graphs.subgraphs.analyst.graph_builders import analyst_graph
from ai_workflow.src.schemas.states import create_initial_state
from ai_workflow.src.configs import GRAPH_CONFIG
from ai_workflow.src.graphs.graph_visulaizers import visualize_graph
from characters.models import Character
import uuid
import traceback
from pathlib import Path
from chunks.models import Chunk

class Command(BaseCommand):
    help = 'Run AI workflow for character extraction from books'

    def add_arguments(self, parser):
        parser.add_argument(
            '--book-id',
            type=str,
            help='Book ID (UUID) to process',
            required=True
        )
        parser.add_argument(
            '--visualize',
            action='store_true',
            help='Visualize the workflow graph before processing'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing characters before processing'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode with detailed error reporting'
        )

    def handle(self, *args, **options):
        book_id = options['book_id']

        # Validate book_id format
        try:
            uuid.UUID(book_id)
        except ValueError as e:
            raise CommandError(f'Invalid book ID format: {book_id}. Expected a valid UUID. Error: {e}')

        self.stdout.write(self.style.SUCCESS(f'Starting AI workflow for book: {book_id}'))

        # Validate dependencies and configurations
        try:
            self._validate_dependencies()
        except Exception as e:
            raise CommandError(f'Dependency validation failed: {e}')

        # Visualize graphs if requested
        if options['visualize']:
            self.stdout.write('Generating graph visualizations...')
            try:
                visualize_graph(orchestrator_graph, "orchestrator")
                visualize_graph(validator_graph, "validator")
                visualize_graph(preprocessor_graph, "preprocessor")
                visualize_graph(analyst_graph, "analyst")
                self.stdout.write(self.style.SUCCESS('Graph visualizations saved!'))
            except ImportError as e:
                self.stdout.write(self.style.ERROR(f'Failed to generate visualizations - Missing dependency: {e}'))
                self.stdout.write(self.style.WARNING('Install required visualization packages: pip install graphviz'))
                if options.get('debug') or self.verbosity >= 2:
                    self.stdout.write(f'Full traceback: {traceback.format_exc()}')
            except FileNotFoundError as e:
                self.stdout.write(self.style.ERROR(f'Failed to generate visualizations - File not found: {e}'))
                if options.get('debug') or self.verbosity >= 2:
                    self.stdout.write(f'Full traceback: {traceback.format_exc()}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to generate visualizations - Unexpected error: {e}'))
                if options.get('debug') or self.verbosity >= 2:
                    self.stdout.write(f'Full traceback: {traceback.format_exc()}')

        # Clear existing characters if requested
        if options['clear_existing']:
            self.stdout.write('Clearing existing characters...')
            try:
                Chunk.objects.filter(book=book_id).delete()
                Character.objects.filter(book=book_id).delete()
                self.stdout.write(self.style.SUCCESS('Existing characters and chunks cleared!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to clear characters - Database error: {e}'))
                if options.get('debug') or self.verbosity >= 2:
                    self.stdout.write(f'Full traceback: {traceback.format_exc()}')
                return

        # Get book and validate file exists
        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            raise CommandError(f'Book with ID {book_id} not found in database')
        except Exception as e:
            raise CommandError(f'Database error while retrieving book {book_id}: {e}')

        if not book.file:
            raise CommandError(f'Book {book_id} has no file attached. Please upload a file first.')
        
        # Validate file exists on filesystem
        if hasattr(book.file, 'path'):
            file_path = Path(book.file.path)
            if not file_path.exists():
                raise CommandError(f'Book file does not exist on filesystem: {file_path}')
            if file_path.stat().st_size == 0:
                raise CommandError(f'Book file is empty: {file_path}')


        # Process the book
        try:
            self.stdout.write('Creating initial state...')
            initial_state = create_initial_state(book_id=book_id)
            self.stdout.write('Initial state created successfully.')

            self.stdout.write('Invoking AI workflow graph...')
            result = orchestrator_graph.invoke(initial_state, config=GRAPH_CONFIG)

            self.stdout.write(self.style.SUCCESS('Workflow completed successfully!'))
            self.stdout.write(f'Result: {result}')

        except ImportError as e:
            error_msg = f'Missing required module or dependency: {e}'
            self.stdout.write(self.style.ERROR(error_msg))
            self.stdout.write(self.style.WARNING('Please ensure all required packages are installed.'))
            if options.get('debug') or self.verbosity >= 2:
                self.stdout.write('Full traceback:')
                self.stdout.write(traceback.format_exc())
            raise CommandError(f'AI workflow execution failed - {error_msg}')
        
        except AttributeError as e:
            error_msg = f'Configuration or method error: {e}'
            self.stdout.write(self.style.ERROR(error_msg))
            if 'objects' in str(e):
                self.stdout.write(self.style.WARNING('This might be a serialization issue with the state objects.'))
            if options.get('debug') or self.verbosity >= 2:
                self.stdout.write('Full traceback:')
                self.stdout.write(traceback.format_exc())
            raise CommandError(f'AI workflow execution failed - {error_msg}')
        
        except KeyError as e:
            error_msg = f'Missing required configuration key: {e}'
            self.stdout.write(self.style.ERROR(error_msg))
            self.stdout.write(self.style.WARNING('Check GRAPH_CONFIG and state configuration.'))
            if options.get('debug') or self.verbosity >= 2:
                self.stdout.write('Full traceback:')
                self.stdout.write(traceback.format_exc())
            raise CommandError(f'AI workflow execution failed - {error_msg}')
        
        except TypeError as e:
            error_msg = f'Type mismatch or invalid arguments: {e}'
            self.stdout.write(self.style.ERROR(error_msg))
            if 'objects' in str(e):
                self.stdout.write(self.style.WARNING('This might be a serialization issue with graph state objects.'))
            if options.get('debug') or self.verbosity >= 2:
                self.stdout.write('Full traceback:')
                self.stdout.write(traceback.format_exc())
            raise CommandError(f'AI workflow execution failed - {error_msg}')
        
        except Exception as e:
            error_msg = f'Unexpected error: {type(e).__name__}: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            
            # Provide more context for common issues
            if 'objects' in str(e).lower():
                self.stdout.write(self.style.WARNING('This appears to be a serialization/deserialization issue.'))
                self.stdout.write(self.style.WARNING('Check that all state objects are properly serializable.'))
            
            if options.get('debug') or self.verbosity >= 2:
                self.stdout.write('Full traceback:')
                self.stdout.write(traceback.format_exc())
            else:
                self.stdout.write('Run with --debug or --verbosity=2 for full traceback.')
                
            raise CommandError(f'AI workflow execution failed - {error_msg}')

    def _validate_dependencies(self):
        """Validate that all required dependencies and configurations are available."""
        try:
            # Test imports
            from ai_workflow.src.graphs.orhcestrator.graph_builders import orchestrator_graph
            from ai_workflow.src.schemas.states import create_initial_state
            from ai_workflow.src.configs import GRAPH_CONFIG
            
            # Test that graph is properly configured
            if not hasattr(orchestrator_graph, 'invoke'):
                raise AttributeError("orchestrator_graph does not have invoke method")
            
            # Test that config exists and has required structure
            if not GRAPH_CONFIG:
                raise ValueError("GRAPH_CONFIG is empty or None")
                
        except ImportError as e:
            raise ImportError(f"Failed to import required module: {e}")
        except Exception as e:
            raise Exception(f"Dependency validation error: {e}")


