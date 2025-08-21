from ai_workflow.src.preprocessors.text_checkers import ArabicLanguageDetector
from ai_workflow.src.schemas.states import State
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.preprocessors.text_splitters import get_validation_chunks
from ai_workflow.src.language_models.chains import text_quality_assessment_chain, text_classification_chain, empty_profile_validation_chain
from books.models import Book
from utils.websocket_events import create_validation_error_event, create_validation_success_event, create_unexpected_error_event
import logging

logger = logging.getLogger(__name__)
        
def language_checker(state : State):
    """
    Node that Checks the text langauge of the file before cleaning.
    Uses the check_text function to make sure the input text is in Arabic.
    Supports both EPUB and plain text files.
    """

    book = Book.objects.get(book_id=state['book_id'])
    file_path = book.txt_file.path
    detector = ArabicLanguageDetector()
    result = detector.check_text(file_path)
    book.detected_language = result
    book.save()
    
    # Send validation result via standardized event
    if 'progress_callback' in state:
        if result != "ar":
            error_event = create_validation_error_event(
                validation_stage="language_check",
                error_code="LANGUAGE_NOT_SUPPORTED",
                message="لغة الكتاب غير مدعومة",
                details="يدعم النظام حاليًا الكتب باللغة العربية فقط",
                user_action="يرجى رفع كتاب باللغة العربية"
            )
            state['progress_callback'](error_event)
            return
    
    return

    

def text_quality_assessor(state):
    """
    Node that assesses the quality of Arabic text using Gemini AI.
    """
    book = Book.objects.get(book_id=state['book_id'])
    file_path = book.txt_file.path

    formatted_chunks = get_validation_chunks(file_path,  chunk_size=30, num_chunks_to_select=5)
    
    chain_input = {
        "text": formatted_chunks
    }
    
    response = text_quality_assessment_chain.invoke(chain_input)
    
    assessment = {
        "quality_score": response.quality_score,
        "quality_level": response.quality_level,
        "issues": response.issues,
        "suggestions": response.suggestions,
        "reasoning": response.reasoning
    }
    book.quality_score = assessment["quality_score"]
    book.save()
    
    # Send validation result via standardized event
    if 'progress_callback' in state:
        if assessment["quality_score"] < 0.5:
            # Send validation error event
            error_event = create_validation_error_event(
                validation_stage="text_quality",
                error_code="POOR_TEXT_QUALITY",
                message="جودة النص منخفضة",
                details=f"درجة الجودة: {assessment['quality_score']:.2f}. الحد الأدنى المطلوب: 0.5",
                user_action="يرجى رفع كتاب بجودة نص أفضل"
            )
            state['progress_callback'](error_event)
            return
        
    return


def text_classifier(state: State):
    """
    Node that classifies the input text as literary or non-literary using Gemini AI.
    """
    book = Book.objects.get(book_id=state['book_id'])
    file_path = book.txt_file.path
    formatted_chunks = get_validation_chunks(file_path, chunk_size=30, num_chunks_to_select=5)
    
    chain_input = {
        "text": formatted_chunks
    }
    
    response = text_classification_chain.invoke(chain_input)
    
    classification = {
        "is_literary": response.is_literary,
        "classification": response.classification,
        "confidence": response.confidence,
        "reasoning": response.reasoning,
        "literary_features": response.literary_features,
        "non_literary_features": response.non_literary_features
    }
    book.text_classification = classification
    book.save()
    
    # Send validation result via standardized event
    if 'progress_callback' in state:
        if not classification["is_literary"]:
            # Send validation error event
            error_event = create_validation_error_event(
                validation_stage="book_classification",
                error_code="INVALID_GENRE",
                message="نوع الكتاب غير مدعوم",
                details="يدعم النظام حاليًا الكتب الأدبية فقط (روايات، قصص، إلخ)",
                user_action="يرجى رفع كتاب أدبي (رواية أو مجموعة قصصية)"
            )
            state['progress_callback'](error_event)
            return
    
    # If all validations passed, send success event
    if 'progress_callback' in state and classification["is_literary"]:
        success_event = create_validation_success_event()
        state['progress_callback'](success_event)
    
    return


