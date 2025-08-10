from typing import TypedDict
from langgraph.graph.message import add_messages
from ai_workflow.src.databases.database import CharacterDatabase
from ai_workflow.src.schemas.data_classes import Profile, LastAppearingCharacter, TextQualityAssessment, TextClassification, ProfileValidation

class State(TypedDict):
    file_path: str
    cleaned_text: str
    content_text: str
    chunk_generator: object
    current_chunk: str
    previous_chunk: str
    last_profiles: list[Profile] | None
    last_appearing_characters: list[LastAppearingCharacter] | None
    database: CharacterDatabase
    no_more_chunks: bool
    is_arabic : bool
    last_summary: str
    text_quality_assessment: TextQualityAssessment | None
    text_classification: TextClassification | None
    profile_validation: ProfileValidation | None

initial_state = {
    'file_path': 'ai_workflow/resources/texts/اللص والكلاب.txt',
    'cleaned_text': '',
    'content_text': '',
    'chunk_generator': None,
    'current_chunk': '',
    'previous_chunk': '',
    'last_profiles': None,
    'last_appearing_characters': None,
    'database': CharacterDatabase(),
    'no_more_chunks': False,
    'last_summary': '',
    'text_quality_assessment': None,
    'text_classification': None,
    'profile_validation': None
    
}
