from typing import TypedDict, Optional, Any
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
    prohibited_content: bool
    last_profiles_by_name: dict[str, list[Character]] | None   
    summary_status: str
    job_id: str
    pause_signal: Optional[Any]
    from_http: bool

def create_initial_state(book_id: str, job_id: str, from_http: bool):
    """
    Create the initial state
    
    Args:
        book_id: book ID for character context
        progress_callback: callback function for progress updates
    """

    state = {
        'book_id': book_id,
        'job_id': job_id,
        'no_more_chunks': False,
        'last_summary': '',
        'chunk_num': 0,
        'num_of_chunks': 0,
        'validation_passed': True,
        'clean_chunks': [],
        'prohibited_content': False,
        'last_profiles_by_name': None,   
        'last_appearing_names': None,
        'summary_status': '',
        'from_http': from_http
        }
            
    return state


