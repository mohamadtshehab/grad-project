from ai_workflow.src.schemas.states import State
from ai_workflow.src.databases.django_adapter import get_character_adapter
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.language_models.chains import name_query_chain, profile_difference_chain, summary_chain, empty_profile_validation_chain
from utils.websocket_events import create_chunk_ready_event

def first_name_querier(state: State):
    """
    Node that queries the name of the character in the current chunk.
    """
    previous_chunk = state['clean_chunks'][state['chunk_num'] - 1]
    third_of_length_of_previous_chunk = len(previous_chunk)//3
    
    context = str(previous_chunk[2 * third_of_length_of_previous_chunk:])
    
    chain_input = {
        "text": str(context)
    }
    
    response = name_query_chain.invoke(chain_input)
    
    characters = response.names if hasattr(response, 'names') else []
    
    
    return {
        'last_appearing_names': characters
    } 
    
def second_name_querier(state: State):
    """
    Node that queries the name of the character in the last summary.
    """
    context = state['last_summary']
    
    chain_input = {
        "text": str(context)
    }
    
    response = name_query_chain.invoke(chain_input)
    
    
    return {
        'last_appearing_names': response.names
    } 


def profile_retriever_creator(state: State):
    """
    Node that creates a new profile or retrieves an existing one.
    Uses last_appearing_names to retrieve profiles from Django Character models.
    If no character exists, creates a new entry with that name, keeping other profile data null.    
    """
    last_appearing_names = state['last_appearing_names']
    book_id = state.get('book_id')
    
    # Get the Django character adapter with book context
    character_adapter = get_character_adapter(book_id)
    
    characters = []
    
    for character_name in last_appearing_names:
        
        name = character_name if isinstance(character_name, str) else str(character_name)
        
        existing_characters = character_adapter.find_characters_by_name(name)
        
        if existing_characters:
            for char in existing_characters:
                characters.append(Character(
                    id=char['id'],
                    profile=Profile(**char['profile'])
                ))
            
        else:
            new_profile = Profile(name=name)
            
            profile_dict = new_profile.model_dump()
            
            # Insert character and get the generated ID
            character_id = character_adapter.insert_character(profile_dict)
            
            # Create Character object with the new profile
            characters.append(Character(
                id=character_id,
                profile=new_profile
            ))
    
    
    return {'last_profiles': characters}


def profile_refresher(state: State):
    """
    Node that refreshes the profiles based on the current chunk.
    """
    chain_input = {
        "text": str(state['last_summary']),
        "profiles": str([char.profile for char in state['last_profiles']])
    }
    response = profile_difference_chain.invoke(chain_input)
    
    # Get the Django character adapter with book context
    book_id = state.get('book_id')
    character_adapter = get_character_adapter(book_id)
    
    # Update database with new profile data
    updated_characters = []
    for i, profile in enumerate(response.profiles):
        # Get the existing character ID
        existing_character = state['last_profiles'][i]
        
        
        profile_dict = profile.model_dump()
        
        # Update the database using Django adapter
        character_adapter.update_character(existing_character.id, profile_dict)
        
        # Create updated Character object
        updated_characters.append(Character(
            id=existing_character.id,
            profile=profile
        ))
        
    return {
        'last_profiles': updated_characters,
    }

def chunk_updater(state: State):
    """
    Node that updates the previous and current chunks in the state.
    """
    updated_chunk_num = state['chunk_num'] + 1
    
    # Send chunk ready event using standardized structure
    if 'progress_callback' in state:
        chunk_ready_event = create_chunk_ready_event(
            chunk_number=state['chunk_num']  # Current chunk that was just processed
        )
        state['progress_callback'](chunk_ready_event)
    
    if updated_chunk_num == int(state['num_of_chunks']):
        return {
            'no_more_chunks': True,
            'chunk_num': updated_chunk_num
        }
    else:
        return {
                'no_more_chunks': False,
                'chunk_num': updated_chunk_num
            }

    

def summarizer(state: State):
    """
    Node that summarizes the text based on the profiles.
    """
    last_summary = state['last_summary']
    third_of_length_of_last_summary = len(last_summary)//3
    current_chunk = state['clean_chunks'][state['chunk_num']]
    context = str(last_summary[2 * third_of_length_of_last_summary:]) + " " + str(current_chunk)
    
    character_names = state['last_appearing_names']
    
    chain_input = {
        "text": context,
        "names": str(character_names)
    }
    response = summary_chain.invoke(chain_input)
        
    return {'last_summary': response.summary}



def empty_profile_validator(state: State):
    """
    Node that validates Empty profiles and Suggest Changes.
    """
    chain_input = {
        "text": str(state['last_summary']),
        "profiles": str([char.profile for char in state['last_profiles']])
    }
    
    response = empty_profile_validation_chain.invoke(chain_input)
    
    empty_profile_validation = EmptyProfileValidation(
        has_empty_profiles= response.has_empty_profiles,
        empty_profiles=response.empty_profiles,
        suggestions=response.suggestions,
        profiles = response.profiles,
        validation_score=response.validation_score
    )
    
    # Get the Django character adapter with book context
    book_id = state.get('book_id')
    character_adapter = get_character_adapter(book_id)
    
    # Update database and create updated Character objects
    updated_characters = []
    for i, profile in enumerate(response.profiles):
        # Get the existing character ID
        existing_character = state['last_profiles'][i]
        
        
        profile_dict = profile.model_dump()
        
        
        # Update the database using Django adapter
        character_adapter.update_character(existing_character.id, profile_dict)
        
        # Create updated Character object
        updated_characters.append(Character(
            id=existing_character.id,
            profile=profile
        ))
    
    
    return {
        'empty_profile_validation': empty_profile_validation,
        'last_profiles': updated_characters
    }

