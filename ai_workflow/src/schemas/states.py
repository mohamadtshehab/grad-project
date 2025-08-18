from typing import TypedDict, Optional
from langgraph.graph.message import add_messages
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.preprocessors.text_splitters import get_validation_chunks
from typing import Callable

class State(TypedDict):
    last_profiles: list[Character] | None
    last_appearing_names: list[str] | None
    book_id: Optional[str]
    no_more_chunks: bool
    last_summary: str
    chunk_num: int
    num_of_chunks: int
    progress_callback: Optional[Callable]
    validation_passed: bool
    clean_chunks: list[str]
    
def create_initial_state(book_id: str, progress_callback: Optional[Callable] = None):
    """
    Create the initial state
    
    Args:
        book_id: book ID for character context
    """
        
    state = {
        'book_id': book_id,
        'no_more_chunks': False,
        'last_summary': '',
        'chunk_num': 0,
        'num_of_chunks': 0,
        'validation_passed': True,
        'clean_chunks': []
        }
    if progress_callback:
        state['progress_callback'] = progress_callback
    return state
