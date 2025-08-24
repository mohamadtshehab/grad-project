from ai_workflow.src.schemas.states import State
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.language_models.chains import name_query_chain, profile_difference_chain, summary_chain, empty_profile_validation_chain
from utils.websocket_events import create_chunk_ready_event
from characters.models import Character as CharacterModel, CharacterRelationship, ChunkCharacter
from books.models import Book
from chunks.models import Chunk
import os
import sys
import django
import re
import unicodedata
import numpy as np
from django.db import transaction
from books.models import Book
import cohere
import json
from dotenv import load_dotenv
load_dotenv()

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
    Node that retrieves existing profiles from Django Character models.
    Uses last_appearing_names to fetch profiles.
    Does not create new characters if not found.
    Stores chunk-character relationships in the database.
    """
    last_appearing_names = state.get('last_appearing_names') or []
    book_id = state.get('book_id')

    # Get the book instance
    book = Book.objects.get(book_id=book_id)

    characters_by_name = {}

    print("=== Retrieving profiles for appearing characters ===")
    for character_name in last_appearing_names:
        name = character_name if isinstance(character_name, str) else str(character_name)

        # Find existing characters by name using Django ORM directly
        existing_characters = CharacterModel.objects.filter(
            book=book,
            profile__name__icontains=name
        )

        profiles_list = []
        if existing_characters.exists():
            for char in existing_characters:
                profiles_list.append(
                    django_to_pydantic_character(char)
                )

        characters_by_name[name] = profiles_list
        print(json.dumps({name: [p.id for p in profiles_list]}, ensure_ascii=False))

    # Store chunk-character relationships (only for existing characters)
    _store_chunk_character_relationships(book, state['chunk_num'], last_appearing_names)

    print("=== Final mapping (name -> profiles) ===")
    print(json.dumps(
        {name: [p.id for p in profiles] for name, profiles in characters_by_name.items()},
        ensure_ascii=False,
        indent=2
    ))

    return {'last_profiles_by_name': characters_by_name}


def get_embedding(text: str) -> np.ndarray:
    cohere_client = cohere.Client()
    response = cohere_client.embed(model="small", texts=[text])
    return np.array(response.embeddings[0])

def profile_to_text(profile) -> str:
    return f"{profile.name} | {profile.role or ''} | events: {', '.join(profile.events)} | " \
           f"relations: {', '.join(profile.relations)} | personality: {', '.join(profile.personality)} | " \
           f"aliases: {', '.join(profile.aliases)}"

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)

_HONORIFICS_REGEX = re.compile(
    r"^(?:ال)?(?:(?:شيخ)|(?:السيد)|(?:سيد)|(?:معلم)|(?:الحاج)|(?:الحاجة)|"
    r"(?:الدكتور)|(?:دكتور)|(?:د\.)|(?:الأستاذ)|(?:الاستاذ)|(?:استاذ))\s+"
)

def _remove_diacritics(s: str) -> str:
    s = s.replace("ـ", "")
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")

def normalize_key(name: str) -> str:
    if not name:
        return ""
    name = str(name).strip().lower()
    name = _remove_diacritics(name)
    name = _HONORIFICS_REGEX.sub("", name)
    name = name.replace(" ", "")
    return name

def safe_str(value):
    if value is None or (isinstance(value, str) and value.strip().lower() in ["none", "null"]):
        return ""
    return value.strip() if isinstance(value, str) else str(value)

def safe_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else []

def merge_list(old_list, new_list):
    old_list = safe_list(old_list)
    new_list = safe_list(new_list)
    return list(set(old_list + new_list)) if new_list else old_list

def merge_relations(old_list, new_list):
    old_list = safe_list(old_list)
    new_list = safe_list(new_list)
    merged = {}
    for rel in old_list + new_list:
        if ":" in rel:
            name, relation = map(str.strip, rel.split(":", 1))
            merged[name] = relation
    return [f"{n}: {r}" for n, r in merged.items()]


def django_to_pydantic_character(django_char) -> 'Character':
    """Convert Django Character model to Pydantic Character"""
    return Character(
        id=str(django_char.character_id),
        profile=Profile(**django_char.profile)
    )

def update_django_from_pydantic(django_char, pydantic_profile: Profile):
    """Update Django model from Pydantic profile"""
    django_char.profile = pydantic_profile.model_dump()
    django_char.save()
    return django_char

def profile_refresher(state, similarity_threshold: float = 0.9):
    last_profiles_by_name = state.get("last_profiles_by_name") or {}
    last_summary = str(state.get("last_summary") or "")
    book_id = state.get("book_id")
    list_of_character_name = state.get("last_appearing_names") or []

    # Separate Django and Pydantic objects for clear data flow
    django_chars_by_name = {}  # Store Django CharacterModel instances
    pydantic_chars_by_name = {name: profiles[:] for name, profiles in last_profiles_by_name.items()}
    
    # Build Django character mapping for database operations
    for name, pydantic_profiles in pydantic_chars_by_name.items():
        django_chars_by_name[name] = []
        for pydantic_char in pydantic_profiles:
            try:
                django_char = CharacterModel.objects.get(character_id=pydantic_char.id)
                django_chars_by_name[name].append(django_char)
            except CharacterModel.DoesNotExist:
                print(f"⚠️ Django character {pydantic_char.id} not found")
    
    flat_profiles = [ch for profiles in pydantic_chars_by_name.values() for ch in profiles]

    chain_input = {
        "text": last_summary,
        "profiles": [ch.profile.model_dump() for ch in flat_profiles],
        "list_of_character_name": list_of_character_name,
    }
    
    response = profile_difference_chain.invoke(chain_input)
    if not response or not hasattr(response, "profiles"):
        return {"last_profiles_by_name": pydantic_chars_by_name}

    embeddings_cache_by_key = {}
    for key_name, profiles_list in pydantic_chars_by_name.items():
        embeddings_cache_by_key[key_name] = {}
        for ch in profiles_list:
            embeddings_cache_by_key[key_name][ch.id] = get_embedding(profile_to_text(ch.profile))

    book = Book.objects.get(book_id=book_id)
    updated_characters = []

    with transaction.atomic():
        for new_profile_data in response.profiles:
            model_name_raw = safe_str(new_profile_data.name)
            model_key_norm = normalize_key(model_name_raw)

            matched_key = None
            for key_name in pydantic_chars_by_name.keys():
                if normalize_key(key_name) == model_key_norm:
                    matched_key = key_name
                    break

            if matched_key is None:
                matched_key = model_name_raw
                if matched_key not in pydantic_chars_by_name:
                    pydantic_chars_by_name[matched_key] = []
                    django_chars_by_name[matched_key] = []
                    embeddings_cache_by_key[matched_key] = {}

            pydantic_profiles_list = pydantic_chars_by_name.get(matched_key, [])
            django_profiles_list = django_chars_by_name.get(matched_key, [])
            matched_profile = None
            new_name_norm = normalize_key(model_name_raw)

            for existing_char in pydantic_profiles_list:
                names_to_check = [existing_char.profile.name] + safe_list(existing_char.profile.aliases)
                names_norm = [normalize_key(n) for n in names_to_check]
                if new_name_norm in names_norm:
                    matched_profile = existing_char
                    break

            if matched_profile is None and pydantic_profiles_list:
                new_emb = get_embedding(profile_to_text(new_profile_data))
                best_match = None
                best_sim = 0.0
                for existing_char in pydantic_profiles_list:
                    existing_emb = embeddings_cache_by_key[matched_key].get(existing_char.id)
                    if existing_emb is None:
                        existing_emb = get_embedding(profile_to_text(existing_char.profile))
                        embeddings_cache_by_key[matched_key][existing_char.id] = existing_emb
                    sim = cosine_similarity(new_emb, existing_emb)
                    if sim > best_sim:
                        best_sim = sim
                        best_match = existing_char
                if best_match is not None and best_sim >= similarity_threshold:
                    matched_profile = best_match

            if matched_profile is not None:
                existing_char = matched_profile
                merged_profile = Profile(
                    name=safe_str(existing_char.profile.name),
                    age=safe_str(new_profile_data.age or existing_char.profile.age),
                    role=safe_str(new_profile_data.role or existing_char.profile.role),
                    events=merge_list(existing_char.profile.events, new_profile_data.events),
                    relations=merge_relations(existing_char.profile.relations, new_profile_data.relations),
                    aliases=merge_list(
                        existing_char.profile.aliases,
                        [model_name_raw] if model_name_raw != existing_char.profile.name else []
                    ),
                    physical_characteristics=merge_list(
                        existing_char.profile.physical_characteristics,
                        new_profile_data.physical_characteristics
                    ),
                    personality=merge_list(
                        existing_char.profile.personality,
                        new_profile_data.personality
                    ),
                )
                # Update Django model
                django_character = CharacterModel.objects.get(character_id=existing_char.id)
                update_django_from_pydantic(django_character, merged_profile)
                
                # Update Pydantic object in list
                char_index = pydantic_profiles_list.index(existing_char)
                pydantic_profiles_list[char_index] = Character(id=existing_char.id, profile=merged_profile)

            else:
                merged_profile = Profile(
                    name=safe_str(model_name_raw),
                    age=safe_str(new_profile_data.age),
                    role=safe_str(new_profile_data.role),
                    events=safe_list(new_profile_data.events),
                    relations=safe_list(new_profile_data.relations),
                    aliases=safe_list(new_profile_data.aliases),
                    physical_characteristics=safe_list(new_profile_data.physical_characteristics),
                    personality=safe_list(new_profile_data.personality),
                )
                # Create new Django character
                django_character = CharacterModel.objects.create(
                    book=book,
                    profile=merged_profile.model_dump()
                )
                # Create new Pydantic character and add to list
                pydantic_character = Character(id=str(django_character.character_id), profile=merged_profile)
                pydantic_profiles_list.append(pydantic_character)
                django_profiles_list.append(django_character)
                embeddings_cache_by_key[matched_key][str(django_character.character_id)] = get_embedding(profile_to_text(merged_profile))

            # Update the mappings
            pydantic_chars_by_name[matched_key] = pydantic_profiles_list
            django_chars_by_name[matched_key] = django_profiles_list

        _store_character_relationships(book, [ch.profile for plist in pydantic_chars_by_name.values() for ch in plist])

    return {"last_profiles_by_name": pydantic_chars_by_name}


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
        
        # Update the database using Django ORM directly
        django_character = CharacterModel.objects.get(character_id=existing_character.id)
        update_django_from_pydantic(django_character, profile)
        
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
                    profile__name__icontains=character_name
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
                    profile__name=profile.name
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
                                profile__name=other_name
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
                                print(f"✓ Created relationship: {from_char.profile['name']} <-> {to_char.profile['name']} ({relationship_type})")
                            else:
                                print(f"↻ Updated relationship: {from_char.profile['name']} <-> {to_char.profile['name']} ({relationship_type})")
                                
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

