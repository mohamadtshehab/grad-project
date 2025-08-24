"""
Refactored analyst nodes using the new modular service architecture.
This version maintains backward compatibility while using improved services.
"""
import logging
from typing import Dict, List, Any

from ai_workflow.src.django_init import setup_django
setup_django()

# Import after Django setup
from ai_workflow.src.schemas.states import State
from ai_workflow.src.schemas.output_structures import EmptyProfileValidation, Character
from ai_workflow.src.services.db_services import (
    CharacterDBService, ChunkCharacterService, CharacterRelationshipService, ChunkDBService,
    django_to_pydantic_character
)
from ai_workflow.src.services.ai_services import AIChainService
from ai_workflow.src.services.profile_processor import ProfileProcessor
from ai_workflow.src.services.utils import SIMILARITY_THRESHOLD
from ai_workflow.src.configs import LOG_FORMAT, LOG_LEVEL
from utils.websocket_events import create_chunk_ready_event
from books.models import Book

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def first_name_querier(state: State) -> Dict[str, List[str]]:
    """
    Node that queries character names in the current chunk.
    Refactored to use AI service.
    """
    logger.info("Extracting character names from current chunk")
    
    previous_chunk = state['clean_chunks'][state['chunk_num'] - 1]
    third_of_length = len(previous_chunk) // 3
    context = str(previous_chunk[2 * third_of_length:])
    
    characters = AIChainService.extract_character_names(context)
    
    logger.info(f"Found {len(characters)} character names")
    return {'last_appearing_names': characters}


def second_name_querier(state: State) -> Dict[str, List[str]]:
    """
    Node that queries character names in the last summary.
    Refactored to use AI service.
    """
    logger.info("Extracting character names from summary")
    
    context = state['last_summary']
    characters = AIChainService.extract_character_names(context)
    
    logger.info(f"Found {len(characters)} character names in summary")
    return {'last_appearing_names': characters}


def profile_retriever_creator(state: State) -> Dict[str, Dict[str, List[Character]]]:
    """
    Node that retrieves existing profiles from Django Character models.
    Refactored to use optimized database service.
    """
    last_appearing_names = state.get('last_appearing_names') or []
    book_id = state.get('book_id')
    
    logger.info(f"Retrieving profiles for {len(last_appearing_names)} characters")
    
    # Get the book instance
    book = Book.objects.get(book_id=book_id)
    
    # Use optimized bulk query service
    characters_by_name_django = CharacterDBService.get_characters_by_names_and_book(
        book, last_appearing_names
    )
    
    # Convert to Pydantic characters
    characters_by_name = {}
    for name, django_chars in characters_by_name_django.items():
        pydantic_chars = [django_to_pydantic_character(char) for char in django_chars]
        characters_by_name[name] = pydantic_chars
        logger.info(f"Retrieved {len(pydantic_chars)} profiles for '{name}'")
    
    # Store chunk-character relationships
    ChunkCharacterService.store_chunk_character_relationships(
        book, state['chunk_num'], last_appearing_names
    )
    
    logger.info("Profile retrieval completed")
    return {'last_profiles_by_name': characters_by_name}


def profile_refresher(state: State) -> Dict[str, Dict[str, List[Character]]]:
    """
    Node that refreshes character profiles using AI analysis.
    Refactored to use ProfileProcessor service for better maintainability.
    """
    logger.info("Starting profile refresh process")
    
    last_profiles_by_name = state.get("last_profiles_by_name") or {}
    last_summary = str(state.get("last_summary") or "")
    book_id = state.get("book_id")
    list_of_character_name = state.get("last_appearing_names") or []
    
    # Use the new ProfileProcessor service
    processor = ProfileProcessor(similarity_threshold=SIMILARITY_THRESHOLD)
    updated_profiles = processor.process_profile_updates(
        last_profiles_by_name, last_summary, book_id, list_of_character_name
    )
    
    # Store character relationships
    book = Book.objects.get(book_id=book_id)
    all_profiles = [char.profile for profiles in updated_profiles.values() for char in profiles]
    CharacterRelationshipService.store_character_relationships(book, all_profiles)
    
    logger.info("Profile refresh completed")
    return {"last_profiles_by_name": updated_profiles}


def chunk_updater(state: State) -> Dict[str, Any]:
    """
    Node that updates the chunk counter and sends progress events.
    """
    updated_chunk_num = state['chunk_num'] + 1
    
    logger.info(f"Processing chunk {state['chunk_num']} -> {updated_chunk_num}")
    
    # Send chunk ready event
    if 'progress_callback' in state:
        # Get the chunk_id from the database using book_id and chunk_num
        chunk_id = ChunkDBService.get_chunk_id_by_book_and_number(
            book_id=state['book_id'],
            chunk_number=state['chunk_num']
        )
            
        chunk_ready_event = create_chunk_ready_event(
            chunk_number=state['chunk_num'],  # Current chunk that was just processed
            chunk_id=chunk_id
        )
        state['progress_callback'](chunk_ready_event)
        logger.info(f"Progress event sent for chunk {state['chunk_num']}")
    
    if updated_chunk_num == int(state['num_of_chunks']):
        logger.info("Workflow complete - all chunks processed")
        return {
            'no_more_chunks': True,
            'chunk_num': updated_chunk_num
        }
    else:
        logger.info(f"Continuing to chunk {updated_chunk_num}")
        return {
            'no_more_chunks': False,
            'chunk_num': updated_chunk_num
        }


def summarizer(state: State) -> Dict[str, Any]:
    """
    Node that generates text summaries using AI service.
    """
    
    last_summary = state['last_summary']
    third_of_length = len(last_summary) // 3
    current_chunk = state['clean_chunks'][state['chunk_num']]
    
    # Prepare context
    context = str(last_summary[2 * third_of_length:]) + " " + str(current_chunk)
    character_names = state['last_appearing_names']
    
    # Generate summary using AI service
    summary = AIChainService.generate_summary(context, character_names)
    
    if summary is None:
        logger.warning("Summary generation blocked for prohibited content")
        return {'prohibited_content': True}
    
    logger.info("Summary generated successfully")
    return {'last_summary': summary}


def empty_profile_validator(state: State) -> Dict[str, Any]:
    """
    Node that validates empty profiles and suggests improvements.
    Refactored to use AI service and bulk database operations.
    """
    logger.info("Validating empty profiles")
    
    # Prepare validation input
    profiles_text = [char.profile for char in state['last_profiles']]
    
    # Use AI service for validation
    response = AIChainService.validate_empty_profiles(
        str(state['last_summary']), profiles_text
    )
    
    if not response:
        logger.error("Profile validation failed")
        return {'empty_profile_validation': None, 'last_profiles': state['last_profiles']}
    
    # Create validation result
    empty_profile_validation = EmptyProfileValidation(
        has_empty_profiles=response.has_empty_profiles,
        empty_profiles=response.empty_profiles,
        suggestions=response.suggestions,
        profiles=response.profiles,
        validation_score=response.validation_score
    )
    
    # Bulk update characters
    book_id = state.get('book_id')
    book = Book.objects.get(book_id=book_id)
    
    # Prepare bulk updates
    characters_and_profiles = []
    updated_characters = []
    
    for i, profile in enumerate(response.profiles):
        existing_character = state['last_profiles'][i]
        
        # Get Django character
        django_chars = CharacterDBService.get_characters_by_ids([existing_character.id])
        django_character = django_chars.get(existing_character.id)
        
        if django_character:
            characters_and_profiles.append((django_character, profile))
            updated_characters.append(Character(
                id=existing_character.id,
                profile=profile
            ))
    
    # Perform bulk update
    if characters_and_profiles:
        CharacterDBService.bulk_update_characters(characters_and_profiles)
        logger.info(f"Updated {len(characters_and_profiles)} character profiles")
    
    # Store relationships
    CharacterRelationshipService.store_character_relationships(book, response.profiles)
    
    logger.info("Profile validation completed")
    return {
        'empty_profile_validation': empty_profile_validation,
        'last_profiles': updated_characters
    }

