from ai_workflow.src.preprocessors.text_checkers import ArabicLanguageDetector
from ai_workflow.src.schemas.states import State
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.preprocessors.text_splitters import get_validation_chunks
from ai_workflow.src.language_models.chains import text_quality_assessment_chain, text_classification_chain, empty_profile_validation_chain
from books.models import Book
        
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
    
    # Send progress notification if callback available
    if 'progress_callback' in state:
        state['progress_callback'](
            event_type="validation_progress",
            node_name="language_checker",
            result={
                "is_arabic": result,
                "language": "ar" if result else "unknown",
                "passed": result
            }
        )
    
    return {'result': result}
    

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
    # Send progress notification if callback available
    if 'progress_callback' in state:
        state['progress_callback'](
            event_type="validation_progress",
            node_name="text_quality_assessor",
            result={
                "quality_score": assessment["quality_score"],
                "quality_level": assessment["quality_level"],
                "passed": assessment["quality_score"] >= 0.5  # Adjust threshold as needed
            }
        )
    
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
    
    # Send progress notification if callback available  
    if 'progress_callback' in state:
        state['progress_callback'](
            event_type="validation_progress",
            node_name="text_classifier", 
            result={
                "is_literary": classification["is_literary"],
                "classification": classification["classification"],
                "confidence": classification["confidence"]
            }
        )
    
    return


