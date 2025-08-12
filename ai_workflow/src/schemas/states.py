from typing import TypedDict
from langgraph.graph.message import add_messages
from ai_workflow.src.databases.database import CharacterDatabase
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.utils import get_validation_chunks

class State(TypedDict):
    file_path: str
    cleaned_text: str
    content_text: str
    chunk_generator: object
    current_chunk: str
    previous_chunk: str
    input_validation_chunks: str
    last_profiles: list[Character] | None
    last_appearing_characters: list[Character] | None
    database: CharacterDatabase
    no_more_chunks: bool
    is_arabic : bool
    last_summary: str
    text_quality_assessment: TextQualityAssessment | None
    text_classification: TextClassification | None
    empty_profile_validation: EmptyProfileValidation | None

def create_initial_state():
    """Create the initial state with validation chunks generated."""
    
    file_path = 'ai_workflow/resources/texts/اللص والكلاب.txt'
    
    try:
        input_validation_chunks = get_validation_chunks(file_path)
    except FileNotFoundError:
        input_validation_chunks = ""
    
    return {
        'file_path': file_path,
        'cleaned_text': '',
        'content_text': '',
        'chunk_generator': None,
        'current_chunk': '',
        'previous_chunk': '',
        'input_validation_chunks': input_validation_chunks,
        'last_profiles': None,
        'last_appearing_characters': None,
        'database': CharacterDatabase(),
        'no_more_chunks': False,
        'is_arabic': False,
        'last_summary': '',
        'text_quality_assessment': None,
        'text_classification': None,
        'empty_profile_validation': None
    }

initial_state = create_initial_state()
