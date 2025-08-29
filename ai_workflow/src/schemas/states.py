<<<<<<< HEAD
from typing import TypedDict, Optional, Callable
=======
from typing import TypedDict, Optional, Any
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
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
<<<<<<< HEAD
    progress_callback: Optional[Callable]
    prohibited_content: bool
    last_profiles_by_name: dict[str, list[Character]] | None   
    last_appearing_names: list[str] | None 
    summary_status: str

def create_initial_state(book_id: str, progress_callback: Optional[Callable] = None):
=======
    prohibited_content: bool
    last_profiles_by_name: dict[str, list[Character]] | None   
    summary_status: str
    job_id: str
    pause_signal: Optional[Any]
    from_http: bool

def create_initial_state(book_id: str, job_id: str, from_http: bool):
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    """
    Create the initial state
    
    Args:
        book_id: book ID for character context
        progress_callback: callback function for progress updates
    """

    state = {
        'book_id': book_id,
<<<<<<< HEAD
=======
        'job_id': job_id,
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
        'no_more_chunks': False,
        'last_summary': '',
        'chunk_num': 0,
        'num_of_chunks': 0,
        'validation_passed': True,
        'clean_chunks': [],
        'prohibited_content': False,
        'last_profiles_by_name': None,   
        'last_appearing_names': None,
<<<<<<< HEAD
        'summary_status': ''
        }
    
    # Add callback if provided
    if progress_callback:
        state['progress_callback'] = progress_callback
        
    return state
=======
        'summary_status': '',
        'from_http': from_http
        }
            
    return state


>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
