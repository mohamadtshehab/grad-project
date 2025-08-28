from ai_workflow.src.schemas.states import State
from books.models import Book


def router_from_language_checker_to_text_quality_assessor_or_end(state : State):
    """
     Node that routes to the text quality assessor or end based on the response from the language checker.
    """
    book = Book.objects.get(book_id=state['book_id'])
    if book.detected_language == "ar":
        return "text_quality_assessor"
    else:
        state['validation_passed'] = False
        return "END"
    

def router_from_text_quality_assessor_to_text_classifier_or_end(state: State):
    """
    Node that routes to the text classifier or end based on the response from the text quality assessor.
    """
    book = Book.objects.get(book_id=state['book_id'])
    if book.quality_score >= 0.6:
        return 'text_classifier'
    else:
        state['validation_passed'] = False
        return 'END'

