from typing import TypedDict, Optional
from langgraph.graph.message import add_messages
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.preprocessors.text_splitters import get_validation_chunks

class State(TypedDict):
    file_path: str
    cleaned_text: str
    content_text: str
    chunk_generator: object
    current_chunk: str
    previous_chunk: str
    last_profiles: list[Character] | None
    last_appearing_characters: list[Character] | None
    book_id: Optional[str]
    no_more_chunks: bool
    is_arabic : bool
    last_summary: str
    text_quality_assessment: TextQualityAssessment | None
    text_classification: TextClassification | None
    empty_profile_validation: EmptyProfileValidation | None
    chunk_num:int
    num_of_chunks:int

def create_initial_state(book_id: str, file_path: str):
    """
    Create the initial state with validation chunks generated.
    
    Args:
        book_id: Optional book ID for character context (will auto-resolve file path)
        file_path: Optional file path to process (defaults to test file if no book_id)
    """
        
    return {
        'file_path': file_path,
        'cleaned_text': '',
        'content_text': '',
        'chunk_generator': None,
        'current_chunk': '',
        'previous_chunk': '',
        'last_profiles': None,
        'last_appearing_characters': None,
        'book_id': book_id,
        'no_more_chunks': False,
        'is_arabic': False,
        'last_summary': '',
        'text_quality_assessment': None,
        'text_classification': None,
        'empty_profile_validation': None
    }
