from ai_workflow.src.schemas.states import State
from ai_workflow.src.preprocessors.text_splitters import TextChunker
from ai_workflow.src.preprocessors.text_cleaners import clean_arabic_text_comprehensive
from ai_workflow.src.preprocessors.metadata_remover import remove_book_metadata
from ai_workflow.src.configs import CHUNKING_CONFIG, METADATA_REMOVAL_CONFIG
from books.models import Book
from chunks.models import Chunk
from utils.websocket_events import create_preprocessing_complete_event

def chunker(state: State):
    """
    Node that takes the content text from the state and yields chunks using a generator for memory efficiency.
    Only the current chunk is kept in the state.
    """
    book = Book.objects.get(book_id=state['book_id'])
    file_path = book.txt_file.path
            
    chunker = TextChunker(chunk_size=CHUNKING_CONFIG['chunk_size'], chunk_overlap=CHUNKING_CONFIG['chunk_overlap'], file_path=file_path)
    
    chunks = chunker.chunk_text_arabic_optimized()
    
    for i, chunk in enumerate(chunks):
        Chunk.objects.create(
            book=book,
            chunk_text=chunk,
            chunk_number=i,
        )

    return {
        'num_of_chunks': len(chunks),
    }
    
def cleaner(state: State):
    """
    Node that gets raw chunks from database, cleans each one individually,
    and returns the cleaned chunks array in the state.
    """
    book = Book.objects.get(book_id=state['book_id'])
    
    # Get all raw chunks from database, ordered by chunk_number
    raw_chunks = Chunk.objects.filter(book=book).order_by('chunk_number')
    
    if not raw_chunks.exists():
        raise ValueError(f"No chunks found for book {book.book_id}")
    
    cleaned_chunks = []
    for i, chunk in enumerate(raw_chunks):
        cleaned_text = clean_arabic_text_comprehensive(chunk.chunk_text)
        cleaned_chunks.append(cleaned_text)
            
    
    return {
        'clean_chunks': cleaned_chunks
    }


def metadata_remover(state: State):
    """
    Node that removes book metadata from the beginning of the cleaned text.
    Uses the remove_book_metadata function to identify and remove initial metadata sections.
    """
    first_clean_chunk = state['clean_chunks'][0]
        
    first_chunk_without_metadata = remove_book_metadata(first_clean_chunk, METADATA_REMOVAL_CONFIG)
    
    state['clean_chunks'][0] = first_chunk_without_metadata
    
    if 'progress_callback' in state:
        preprocessing_complete_event = create_preprocessing_complete_event(
            total_chunks=len(state['clean_chunks']),
            chunk_size=CHUNKING_CONFIG.get('chunk_size')
        )
        state['progress_callback'](preprocessing_complete_event)

        
    return
