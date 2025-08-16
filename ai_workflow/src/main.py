import os
import sys

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai_workflow.src.graphs.graph_builders import compiled_graph
from ai_workflow.src.schemas.states import create_initial_state
from ai_workflow.src.configs import GRAPH_CONFIG
from ai_workflow.src.graphs.graph_visualizers import visualize_graph
from books.models import Book
from ai_workflow.src.databases.django_adapter import get_character_adapter
from ai_workflow.src.preprocessors.epub.epub_to_txt_converter import EPUBProcessor
import argparse
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Run AI workflow for character extraction')
    parser.add_argument('--book-id', type=str, help='Book ID (UUID) to process - file path will be auto-resolved')
    parser.add_argument('--visualize', action='store_true', help='Visualize the workflow graph')
    parser.add_argument('--clear-existing', action='store_true', help='Clear existing characters before processing')
    
    args = parser.parse_args()
    
    if args.visualize:
        visualize_graph(compiled_graph)
        
    if args.clear_existing:
        adapter = get_character_adapter(args.book_id)
        adapter.clear_database()
    
    # Resolve book and file path
    book = Book.objects.get(book_id=args.book_id)
    if not book.file:
        raise SystemExit(f"Book {args.book_id} has no file attached")
    original_file_path = book.file.path
    
    # Convert EPUB to TXT if needed, then run
    with EPUBProcessor(original_file_path) as txt_file_path:
        initial_state = create_initial_state(book_id=args.book_id, file_path=txt_file_path)
        result = compiled_graph.invoke(initial_state, config=GRAPH_CONFIG)
    