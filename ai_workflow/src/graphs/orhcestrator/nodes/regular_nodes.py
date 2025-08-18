from ai_workflow.src.schemas.states import State
from books.models import Book
from ai_workflow.src.extractors.book_name_extractor import extract_book_name_from_file

def name_extractor(state: State):
    """
    Node that extracts the book name from the file content using LLM.
    Uses the same logic as the existing extract_book_name_from_file function.
    """
    book = Book.objects.get(book_id=state['book_id'])
    filename = book.txt_file.name
    try:
        response = extract_book_name_from_file(book.txt_file.path)
        book.title = response.book_name
        book.save()
    except Exception as e:
        fallback_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        book.title = fallback_name
        book.save()
        
    if 'progress_callback' in state:
        state['progress_callback'](
            event_type="name_extraction_completed",
            node_name="name_extractor",
            result=book.title
        )
    
    return