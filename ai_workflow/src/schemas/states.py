from typing import TypedDict, Optional, Callable
from ai_workflow.src.schemas.output_structures import *

class State(TypedDict):
    last_profiles: list[Character] | None
    last_appearing_names: list[str] | None
    book_id: Optional[str]
    no_more_chunks: bool
    last_summary: str
    chunk_num: int
    num_of_chunks: int
    validation_passed: bool
    clean_chunks: list[str]
    progress_callback: Optional[Callable]
    prohibited_content: bool

def create_initial_state(book_id: str, progress_callback: Optional[Callable] = None):
    """
    Create the initial state
    
    Args:
        book_id: book ID for character context
        progress_callback: callback function for progress updates
    """
        
    state = {
        'book_id': book_id,
        'no_more_chunks': False,
        'last_summary': '',
        'chunk_num': 0,
        'num_of_chunks': 0,
        'validation_passed': True,
        'clean_chunks': [],
        'prohibited_content': False
        }
    
    # Add callback if provided
    if progress_callback:
        state['progress_callback'] = progress_callback
        
    return state
