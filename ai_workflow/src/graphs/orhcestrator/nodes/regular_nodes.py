from ai_workflow.src.schemas.states import State
from books.models import Book
from ai_workflow.src.extractors.book_name_extractor import extract_book_name_from_file
from utils.websocket_events import create_book_extracted_event

def name_extractor(state: State):
    """
    Node that extracts the book name from the file content using LLM.
    Uses the same logic as the existing extract_book_name_from_file function.
    """
    book = Book.objects.get(book_id=state['book_id'])
    response = extract_book_name_from_file(book.txt_file.path)
    book.title = response.book_name
    book.save()
    
    # Send book extracted event using standardized structure
    if 'progress_callback' in state:
        book_extracted_event = create_book_extracted_event(
            book_name=response.book_name,
            confidence=response.confidence if hasattr(response, 'confidence') else None
        )
        state['progress_callback'](book_extracted_event)
    
    return