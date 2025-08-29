from ai_workflow.src.schemas.states import State
from ai_workflow.src.schemas.contexts import Context
from books.models import Book
from ai_workflow.src.extractors.book_name_extractor import extract_book_name_from_file
from utils.websocket_events import create_book_extracted_event, progress_callback
import logging

def name_extractor(state: State):
    """
    Node that extracts the book name from the file content using LLM.
    Uses the same logic as the existing extract_book_name_from_file function.
    """
    book = Book.objects.get(id=state['book_id'])
    response = extract_book_name_from_file(book.txt_file.path)
    book.title = response.book_name # type: ignore
    book.save()
    try:
        book.refresh_from_db()
        logging.warning(f"Successfully saved and refreshed title: {book.title}")
    except Exception as e:
        logging.error(f"Failed to refresh from DB: {e}")
    
    # Send book extracted event using standardized structure
    if state['from_http']:
        book_extracted_event = create_book_extracted_event(
            book_name=response.book_name,  # type: ignore
            confidence=response.confidence if hasattr(response, 'confidence') else None  # type: ignore
        )
        progress_callback(job_id=state['job_id'], event=book_extracted_event)  # type: ignore
    
    return