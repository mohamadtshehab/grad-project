from ai_workflow.src.schemas.states import State
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.language_models.chains import name_query_chain, profile_difference_chain, summary_chain, empty_profile_validation_chain
from utils.websocket_events import create_chunk_ready_event
from characters.models import Character as CharacterModel, CharacterRelationship, ChunkCharacter
from books.models import Book
from chunks.models import Chunk
from ai_workflow.src.services.db_services import ChunkDBService
import os
import sys
import django

# Setup Django environment if not already configured
def setup_django():
    """Initialize Django settings for standalone scripts."""
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation_backend.settings')
        django.setup()

# Initialize Django
setup_django()


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
    
    # Get the book instance
    book = Book.objects.get(book_id=book_id)
    
    characters = []
    
    for character_name in last_appearing_names:
        
        name = character_name if isinstance(character_name, str) else str(character_name)
        
        # Find existing characters by name using Django ORM directly
        existing_characters = CharacterModel.objects.filter(
            book=book,
            character_data__name__icontains=name
        )
        
        if existing_characters.exists():
            for char in existing_characters:
                characters.append(Character(
                    id=str(char.character_id),
                    profile=Profile(**char.character_data)
                ))
            
        else:
            new_profile = Profile(name=name)
            
            profile_dict = new_profile.model_dump()
            
            # Create new character directly with Django ORM
            new_character = CharacterModel.objects.create(
                book=book,
                character_data=profile_dict
            )
            
            # Create Character object with the new profile
            characters.append(Character(
                id=str(new_character.character_id),
                profile=new_profile
            ))
    
    
    # Store chunk-character relationships
    _store_chunk_character_relationships(book, state['chunk_num'], last_appearing_names)
    
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
    
    # Get the book instance
    book_id = state.get('book_id')
    book = Book.objects.get(book_id=book_id)
    
    # Update database with new profile data using Django ORM directly
    updated_characters = []
    for i, profile in enumerate(response.profiles):
        # Get the existing character ID
        existing_character = state['last_profiles'][i]
        
        
        profile_dict = profile.model_dump()
        
        # Update the database using Django ORM directly
        character = CharacterModel.objects.get(character_id=existing_character.id)
        character.character_data = profile_dict
        character.save()
        
        # Create updated Character object
        updated_characters.append(Character(
            id=existing_character.id,
            profile=profile
        ))
        
    # Store character relationships from updated profiles
    _store_character_relationships(book, response.profiles)
    
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
    third_of_length_of_last_summary = len(last_summary) // 3
    current_chunk = state['clean_chunks'][state['chunk_num']]
    context = str(last_summary[2 * third_of_length_of_last_summary:]) + " " + str(current_chunk)
    
    character_names = state['last_appearing_names']
    
    chain_input = {
        "text": context,
        "names": str(character_names)
    }
    response = summary_chain.invoke(chain_input)
        
    if not response or not hasattr(response, 'summary'):
        print("⚠️ Warning: API response blocked for prohibited content.")
        return {'prohibited_content': True}
    
    # If the response is valid, proceed as normal
    return {'last_summary': response.summary}



def empty_profile_validator(state: State):
    """
    Node that validates Empty profiles and Suggest Changes.
    Also stores character relationships directly in the database.
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
    
    # Get the book instance
    book_id = state.get('book_id')
    book = Book.objects.get(book_id=book_id)
    
    # Update database and create updated Character objects
    updated_characters = []
    for i, profile in enumerate(response.profiles):
        # Get the existing character ID
        existing_character = state['last_profiles'][i]
        
        profile_dict = profile.model_dump()
        
        # Update the database using Django ORM directly
        character = CharacterModel.objects.get(character_id=existing_character.id)
        character.character_data = profile_dict
        character.save()
        
        # Create updated Character object
        updated_characters.append(Character(
            id=existing_character.id,
            profile=profile
        ))
    
    # Store character relationships directly in the database
    _store_character_relationships(book, response.profiles)
    
    return {
        'empty_profile_validation': empty_profile_validation,
        'last_profiles': updated_characters
    }


def _store_chunk_character_relationships(book, chunk_number, character_names):
    """
    Helper function to store chunk-character relationships in the database.
    """
    try:
        # Get the actual Chunk object from the database
        chunk = Chunk.objects.get(book=book, chunk_number=chunk_number)
        
        for character_name in character_names:
            try:
                # Find the character by name
                character = CharacterModel.objects.get(
                    book=book,
                    character_data__name__icontains=character_name
                )
                
                # Create or update the chunk-character relationship
                chunk_character, created = ChunkCharacter.objects.update_or_create(
                    chunk=chunk,
                    character=character,
                    defaults={
                        'mention_count': 1,  # Could be enhanced to count actual mentions
                        'position_info': None  # Could be enhanced to store position data
                    }
                )
                
                if created:
                    print(f"✓ Linked character '{character_name}' to chunk {chunk_number}")
                
            except CharacterModel.DoesNotExist:
                # Character doesn't exist yet, skip for now
                print(f"⚠️ Character '{character_name}' not found for chunk {chunk_number}")
                continue
                
    except Chunk.DoesNotExist:
        print(f"⚠️ Chunk {chunk_number} not found in database")


def _store_character_relationships(book, profiles):
    """
    Helper function to extract and store character relationships from profiles.
    """
    relationships_created = 0
    relationships_skipped = 0
    
    for profile in profiles:
        if profile.relations:
            print(f"Processing relationships for character: {profile.name}")
            print(f"Relations found: {profile.relations}")
            
            # Get the character instance
            try:
                character = CharacterModel.objects.get(
                    book=book,
                    character_data__name=profile.name
                )
                
                for relation in profile.relations:
                    if ':' in relation:
                        other_name, relationship_type = relation.split(':', 1)
                        other_name = other_name.strip()
                        relationship_type = relationship_type.strip()
                        
                        print(f"Attempting to create relationship: {profile.name} -> {relationship_type} -> {other_name}")
                        
                        # Find the other character
                        try:
                            other_character = CharacterModel.objects.get(
                                book=book,
                                character_data__name=other_name
                            )
                            
                            # Create or update the relationship
                            # Ensure canonical order (from.id < to.id) to match model constraints
                            if str(character.character_id) < str(other_character.character_id):
                                from_char, to_char = character, other_character
                            else:
                                from_char, to_char = other_character, character
                            
                            relationship, created = CharacterRelationship.objects.update_or_create(
                                from_character=from_char,
                                to_character=to_char,
                                book=book,
                                defaults={
                                    'relationship_type': relationship_type,
                                    'description': f"Relationship from {profile.name} to {other_name}"
                                }
                            )
                            
                            if created:
                                relationships_created += 1
                                print(f"✓ Created relationship: {from_char.character_data['name']} <-> {to_char.character_data['name']} ({relationship_type})")
                            else:
                                print(f"↻ Updated relationship: {from_char.character_data['name']} <-> {to_char.character_data['name']} ({relationship_type})")
                                
                        except CharacterModel.DoesNotExist:
                            # Other character doesn't exist yet, skip for now
                            relationships_skipped += 1
                            print(f"⚠️ Character '{other_name}' not found, skipping relationship")
                            continue
                    else:
                        print(f"⚠️ Invalid relationship format (missing ':'): {relation}")
                            
            except CharacterModel.DoesNotExist:
                # Character not found, skip
                print(f"⚠️ Character '{profile.name}' not found in database")
                continue
        else:
            print(f"No relationships found for character: {profile.name}")
    
    print(f"Relationship processing complete: {relationships_created} created, {relationships_skipped} skipped")

