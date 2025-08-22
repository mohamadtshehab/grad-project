from ai_workflow.src.language_models.prompts import name_query_prompt, profile_update_prompt, summary_prompt, text_quality_assessment_prompt, text_classification_prompt, empty_profile_validation_prompt
from ai_workflow.src.language_models.llms import name_query_llm, profile_update_llm, summary_llm, text_quality_assessment_llm, text_classification_llm, empty_profile_validation_llm
from ai_workflow.src.preprocessors.text_checkers import ArabicLanguageDetector
from ai_workflow.src.schemas.states import State
from ai_workflow.src.preprocessors.text_splitters import TextChunker
from ai_workflow.src.preprocessors.text_cleaners import clean_arabic_text_comprehensive
from ai_workflow.src.preprocessors.metadata_remover import remove_book_metadata
from ai_workflow.src.databases.django_adapter import get_character_adapter
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.language_models.tools import CharacterRoleTool
from ai_workflow.src.preprocessors.epub.epub_extractor import extract_text_from_file
import os 
from ai_workflow.src.preprocessors.text_splitters import get_validation_chunks
import uuid
from rapidfuzz import fuzz
from openai import OpenAI
import numpy as np
from ai_workflow.src.schemas.states import State
from ai_workflow.src.schemas.output_structures import Character, Profile
from typing import List
import cohere
import json
import unicodedata
import re

def language_checker(state : State):
    """
    Node that Checks the text from the file before cleaning.
    Uses the check_text function to make sure the input text is in Arabic.
    Supports both EPUB and plain text files.
    """
    file_path = state['file_path']
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Extract text from file (handles EPUB and plain text)
    raw_text = extract_text_from_file(file_path)
    detector = ArabicLanguageDetector()
    
    result = detector.check_text(raw_text)
    return {
        'is_arabic': result
    }
    
    
def cleaner(state: State):
    """
    Node that cleans the text from the file before chunking.
    Uses the clean_text function to normalize and clean the input text.
    Supports both EPUB and plain text files.
    """
    file_path = state['file_path']
    
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Extract text from file (handles EPUB and plain text)
    raw_text = extract_text_from_file(file_path)

    # Clean the text using the clean_text function
    cleaned_text = clean_arabic_text_comprehensive(raw_text)
    
    return {
        'cleaned_text': cleaned_text
    }


def metadata_remover(state: State):
    """
    Node that removes book metadata from the beginning of the cleaned text.
    Uses the remove_book_metadata function to identify and remove initial metadata sections.
    """
    cleaned_text = state['cleaned_text']
    
    if not cleaned_text:
        raise ValueError("No cleaned text available in state")
    
    # Remove metadata from the cleaned text
    content_text = remove_book_metadata(cleaned_text)
    
    return {
        'content_text': content_text
    }


def chunker(state: State):
    """
    Node that takes the content text from the state and yields chunks using a generator for memory efficiency.
    Only the current chunk is kept in the state.
    """
    content_text = state['content_text']
    
    if not content_text:
        raise ValueError("No content text available in state")
        
    chunker = TextChunker(chunk_size=5000, chunk_overlap=100)
    
    chunks = chunker.chunk_text_arabic_optimized(content_text)

    
    def chunk_generator():
        for chunk in chunks:
            yield chunk
            
    gen = chunk_generator()
        
    return {
    'chunk_generator': gen,
    'num_of_chunks': len(chunks)
}
    
def first_name_querier(state: State):
    """
    Node that queries the name of the character in the current chunk.
    """
    third_of_length_of_previous_chunk = len(state['previous_chunk'])//3
    
    context = str(state['previous_chunk'][2 * third_of_length_of_previous_chunk:]) + " " + str(state['current_chunk'])
    
    chain_input = {
        "text": str(context)
    }
    
    chain = name_query_prompt | name_query_llm
    
    response = chain.invoke(chain_input)
    
    characters = response.characters if hasattr(response, 'characters') else []
    
    return {
        'last_appearing_characters': characters
    } 
    
def second_name_querier(state: State):
    """
    Node that queries the name of the character in the last summary.
    """
    context = state['last_summary']
    
    chain_input = {
        "text": str(context)
    }
    
    chain = name_query_prompt | name_query_llm
    
    response = chain.invoke(chain_input)
    
    return {
        'last_appearing_characters': response.characters
    } 

#test
# def profile_retriever_creator(state: State):
#     last_appearing_characters = state['last_appearing_characters']
#     book_id = state.get('book_id')

#     character_adapter = get_character_adapter(book_id)
#     characters = []

#     # جلب كل الشخصيات الموجودة في الكتاب
#     all_characters = character_adapter.get_all_characters()  # كل عنصر فيه 'id' و 'profile'

#     for character_name in last_appearing_characters:
#         name = character_name if isinstance(character_name, str) else str(character_name)
#         name_lower = name.strip().lower()

#         matched_char = None

#         for char in all_characters:
#             profile = char.get('profile', {})
#             if isinstance(profile, list):
#                     profile = profile[0] if profile else {}
#                     char_name = profile.get('name', "")
#                     aliases = profile.get('aliases', [])

#             char_name_lower = char_name.strip().lower()
#             aliases_lower = [a.strip().lower() for a in aliases]

#             # مطابقة مباشرة
#             if name_lower == char_name_lower or name_lower in aliases_lower:
#                 matched_char = char
#                 break

#             # مطابقة fuzzy جزئية
#             if fuzz.partial_ratio(name_lower, char_name_lower) >= 85:
#                 matched_char = char
#                 break
#             for alias in aliases_lower:
#                 if fuzz.partial_ratio(name_lower, alias) >= 95:
#                     matched_char = char
#                     break
#             if matched_char:
#                 break

#         if matched_char:
#             profile = matched_char['profile']
#             aliases = profile.get('aliases', [])

#             # تحديث aliases إذا الاسم الجديد غير موجود
#             if name not in aliases:
#                 aliases.append(name)
#                 profile['aliases'] = aliases
#                 character_adapter.update_character(matched_char['id'], aliases)

#             characters.append(Character(
#                 id=matched_char['id'],
#                 profile=Profile(**profile)
#             ))
#         else:
#             # إنشاء بروفايل جديد
#             new_profile = Profile(name=name, aliases=[name])
#             profile_dict = new_profile.model_dump()
#             character_id = character_adapter.insert_character(profile_dict)
#             characters.append(Character(
#                 id=character_id,
#                 profile=new_profile
#             ))

#     return {'last_profiles': characters}

#working
# def profile_retriever_creator(state: State):
#     """
#     Node that creates a new profile or retrieves an existing one.
#     Uses last_appearing_characters to retrieve profiles from Django Character models.
#     If no character exists, creates a new entry with that name, keeping other profile data null.    
#     """
#     last_appearing_characters = state['last_appearing_characters']
#     book_id = state.get('book_id')
    
#     # Get the Django character adapter with book context
#     character_adapter = get_character_adapter(book_id)
    
#     characters = []
    
#     for character_name in last_appearing_characters:
        
#         name = character_name if isinstance(character_name, str) else str(character_name)
        
#         existing_characters = character_adapter.find_characters_by_name(name)
        
#         if existing_characters:
#             for char in existing_characters:
#                 characters.append(Character(
#                     id=char['id'],
#                     profile=Profile(**char['profile'])
#                 ))
            
#         else:
#             new_profile = Profile(name=name)
            
#             profile_dict = new_profile.model_dump()
            
#             # Insert character and get the generated ID
#             character_id = character_adapter.insert_character(profile_dict)
            
#             # Create Character object with the new profile
#             characters.append(Character(
#                 id=character_id,
#                 profile=new_profile
#             ))
    
#     return {'last_profiles': characters}


def profile_retriever_creator(state: State): 
    last_appearing_characters = state.get('last_appearing_characters') or [] 
    book_id = state.get('book_id') 
    character_adapter = get_character_adapter(book_id) 
    characters_by_name = {} 

    print("=== Database characters so far ===") 
    all_chars = character_adapter.get_all_characters()  

    for c in all_chars:  
        char_name = c.get('name') or c.get('profile', {}).get('name') 
        print(json.dumps({"id": c['id'], "name": char_name}, ensure_ascii=False))  

    print("=== Retrieving profiles for appearing characters ===") 
    for character_name in last_appearing_characters: 
        name = character_name if isinstance(character_name, str) else str(character_name) 
        existing_characters = character_adapter.find_characters_by_name(name) or [] 
        profiles_list = [
            Character(id=char['id'], profile=Profile(**char['profile'])) 
            for char in existing_characters
        ] 
        characters_by_name[name] = profiles_list 
        print(json.dumps({name: [p.id for p in profiles_list]}, ensure_ascii=False))  

    print("=== Final mapping (name -> profiles) ===") 
    print(json.dumps(
        {name: [p.id for p in profiles] for name, profiles in characters_by_name.items()},
        ensure_ascii=False,
        indent=2
    ))  

    return {'last_profiles_by_name': characters_by_name}


COHERE_API_KEY = os.getenv("COHERE_API_KEY")
cohere_client = cohere.Client(COHERE_API_KEY)

def get_embedding(text: str) -> np.ndarray:
    response = cohere_client.embed(
        model="small",      # نموذج مضمون العمل
        texts=[text]
    )
    return np.array(response.embeddings[0])

def profile_to_text(profile: Profile) -> str:
    return f"{profile.name} | {profile.role or ''} | events: {', '.join(profile.events)} | " \
           f"relations: {', '.join(profile.relations)} | personality: {', '.join(profile.personality)} | " \
           f"aliases: {', '.join(profile.aliases)}"

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)


# ---- Normalization helpers ----

_HONORIFICS_REGEX = re.compile(
    r"^(?:ال)?(?:(?:شيخ)|(?:السيد)|(?:سيد)|(?:معلم)|(?:الحاج)|(?:الحاجة)|"
    r"(?:الدكتور)|(?:دكتور)|(?:د\.)|(?:الأستاذ)|(?:الاستاذ)|(?:استاذ))\s+"
)

def _remove_diacritics(s: str) -> str:
    # يزيل التشكيل والتطويل
    s = s.replace("ـ", "")
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")

def normalize_key(name: str) -> str:
    if not name:
        return ""
    name = str(name).strip().lower()
    name = _remove_diacritics(name)
    name = _HONORIFICS_REGEX.sub("", name)  # إزالة الألقاب في أول الاسم فقط
    name = name.replace(" ", "")
    return name

# ------------------------------------------------

def profile_refresher(state: State, similarity_threshold: float = 0.90):
    # --- Utils ---
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

    # --- Inputs from state ---
    last_profiles_by_name: dict[str, list[Character]] = state.get("last_profiles_by_name") or {}
    last_summary = str(state.get("last_summary") or "")
    book_id = state.get("book_id")
    list_of_character_name = state.get("last_appearing_characters") or []

    character_adapter = get_character_adapter(book_id)

    # نسخة قابلة للتعديل
    updated_by_name: dict[str, list[Character]] = {
        name: profiles[:] for name, profiles in last_profiles_by_name.items()
    }

    # flatten profiles (محتويات الليست فقط)
    flat_profiles = [ch for profiles in updated_by_name.values() for ch in profiles]

    # --- call LLM ---
    chain_input = {
        "text": last_summary,
        "profiles": [ch.profile.model_dump() for ch in flat_profiles],
        "list_of_character_name": list_of_character_name,
    }
    chain = profile_update_prompt | profile_update_llm
    response = chain.invoke(chain_input)
    if not response or not hasattr(response, "profiles"):
     return {"last_profiles_by_name": updated_by_name}

    # --- Build embedding cache ---
    embeddings_cache_by_key: dict[str, dict[str, np.ndarray]] = {}
    for key_name, profiles_list in updated_by_name.items():
        embeddings_cache_by_key[key_name] = {}
        for ch in profiles_list:
            embeddings_cache_by_key[key_name][ch.id] = get_embedding(profile_to_text(ch.profile))

    # --- Main processing ---
    for new_profile_data in response.profiles:
        model_name_raw = safe_str(new_profile_data.name)
        model_key_norm = normalize_key(model_name_raw)

        # 1) محاولة التطابق مع المفاتيح (normalized)
        matched_key = None
        for key_name in updated_by_name.keys():
            if normalize_key(key_name) == model_key_norm:
                matched_key = key_name
                break

        # إذا ما في مفتاح مطابق → أنشئ مفتاح جديد
        if matched_key is None:
            matched_key = model_name_raw
            if matched_key not in updated_by_name:
                updated_by_name[matched_key] = []
                embeddings_cache_by_key[matched_key] = {}

        profiles_list = updated_by_name.get(matched_key, [])

        # 2) داخل الليست الخاصة بهذا المفتاح
        matched_profile: Character | None = None
        new_name_norm = normalize_key(model_name_raw)

        # 2.a) تطابق حرفي مع الاسم أو أي alias
        for existing_char in profiles_list:
            names_to_check = [existing_char.profile.name] + safe_list(existing_char.profile.aliases)
            names_norm = [normalize_key(n) for n in names_to_check]
            if new_name_norm in names_norm:
                matched_profile = existing_char
                break
    
    # 2.b) If there is no exact match → we try the embedding similarity within this list only
        if matched_profile is None and profiles_list:
            new_emb = get_embedding(profile_to_text(new_profile_data))
            best_match = None
            best_sim = 0.0
            for existing_char in profiles_list:
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

        # 3) merge or create 
        if matched_profile is not None:
            # --- Merge with existing profile ---
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
            character_id = existing_char.id
            idx = profiles_list.index(existing_char)
            profiles_list[idx] = Character(id=character_id, profile=merged_profile)

            # update DB
            character_adapter.update_character(character_id, merged_profile.model_dump())

        else:
            # --- Create new profile ---
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
            character_dict = merged_profile.model_dump()
            character_id = character_adapter.insert_character(character_dict)
            profiles_list.append(Character(id=character_id, profile=merged_profile))

            # update cache  
            embeddings_cache_by_key[matched_key][character_id] = get_embedding(profile_to_text(merged_profile))

            # update DB
            character_adapter.update_character(character_id, character_dict)

        updated_by_name[matched_key] = profiles_list

    return {"last_profiles_by_name": updated_by_name}



#working
# def profile_refresher(state: State):
#     """
#     Refreshes profiles based on the current chunk.
#     Merges updates returned by the LLM with existing profiles.
#     Ensures no None/null values in output.
#     Relations are merged intelligently: last relation for each character is kept.
#     """

#     def safe_str(value):
#         if value is None or (isinstance(value, str) and value.strip().lower() in ["none", "null"]):
#             return ""
#         return value.strip() if isinstance(value, str) else str(value)

#     def safe_list(value):
#         if value is None:
#             return []
#         return value if isinstance(value, list) else []

#     def merge_list(old_list, new_list):
#         old_list = safe_list(old_list)
#         new_list = safe_list(new_list)
#         return list(set(old_list + new_list)) if new_list else old_list

#     def merge_relations(old_list, new_list):
#         old_list = safe_list(old_list)
#         new_list = safe_list(new_list)
#         merged_dict = {}

#         for rel in old_list:
#             if ':' in rel:
#                 name, relation = map(str.strip, rel.split(':', 1))
#                 merged_dict[name] = relation

#         for rel in new_list:
#             if ':' in rel:
#                 name, relation = map(str.strip, rel.split(':', 1))
#                 merged_dict[name] = relation  

#         return [f"{name}: {relation}" for name, relation in merged_dict.items()]

#     character_role_tool = CharacterRoleTool()
#     chain_input = {
#         "text": str(state['last_summary']),
#         "profiles": str([char.profile for char in state['last_profiles']])
#     }

#     chain = profile_update_prompt | profile_update_llm
#     response = chain.invoke(chain_input)
    
#     # Get the Django character adapter with book context
#     book_id = state.get('book_id')
#     character_adapter = get_character_adapter(book_id)
    
#     # Create mapping of existing characters by index for merging
#     updated_characters = []
    
#     # Process each profile update from LLM response
#     for i, new_profile_data in enumerate(response.profiles):
#         # Get the corresponding existing character
#         if i < len(state['last_profiles']):
#             existing_character = state['last_profiles'][i]
#             old_profile = existing_character.profile

#             # Merge old and new profile data intelligently
#             name = safe_str(new_profile_data.name or old_profile.name)
#             age = safe_str(new_profile_data.age or old_profile.age)
#             role = safe_str(new_profile_data.role) or safe_str(old_profile.role)
            
#             events = merge_list(old_profile.events, new_profile_data.events)
#             relations = merge_relations(old_profile.relations, new_profile_data.relations)
#             aliases = merge_list(old_profile.aliases, new_profile_data.aliases)
#             physical_characteristics = merge_list(old_profile.physical_characteristics, new_profile_data.physical_characteristics)
#             personality = merge_list(old_profile.personality, new_profile_data.personality)

#             # Create merged Profile object
#             merged_profile = Profile(
#                 name=name,
#                 age=age,
#                 role=role,
#                 events=events,
#                 relations=relations,
#                 aliases=aliases,
#                 physical_characteristics=physical_characteristics,
#                 personality=personality
#             )
            
#             character_id = existing_character.id
#         else:
#             # This shouldn't happen normally, but handle new profiles just in case
#             role_value = safe_str(new_profile_data.role)
            
#             merged_profile = Profile(
#                 name=safe_str(new_profile_data.name),
#                 age=safe_str(new_profile_data.age),
#                 role=role_value,
#                 events=safe_list(new_profile_data.events),
#                 relations=safe_list(new_profile_data.relations),
#                 aliases=safe_list(new_profile_data.aliases),
#                 physical_characteristics=safe_list(new_profile_data.physical_characteristics),
#                 personality=safe_list(new_profile_data.personality)
#             )
            
#             # This would be a new character case - use a placeholder ID
#             character_id = f"new_{i}"
        
#         # Convert to dict for database update
#         profile_dict = merged_profile.model_dump()
        
#         # Update the database using Django adapter
#         try:
#            uuid_obj = uuid.UUID(character_id)
#            character_id = str(uuid_obj)
#         except ValueError:
#           character_id = str(uuid.uuid4()) 
     
#         character_adapter.update_character(character_id, profile_dict)
        
#         # Create updated Character object
#         updated_characters.append(Character(
#             id=character_id,
#             profile=merged_profile
#         ))
    
#     return {
#         'last_profiles': updated_characters,
#     }


# def profile_refresher(state: State):
#     """
#     Refreshes profiles based on the current chunk.
#     Merges updates returned by the LLM with existing profiles.
#     Ensures no None/null values in output.
#     Relations are merged intelligently: last relation for each character is kept.
#     Uses id matching first; falls back to name matching if id is missing.
#     """

#     def safe_str(value):
#         if value is None or (isinstance(value, str) and value.strip().lower() in ["none", "null"]):
#             return ""
#         return value.strip() if isinstance(value, str) else str(value)

#     def safe_list(value):
#         if value is None:
#             return []
#         return value if isinstance(value, list) else []

#     def merge_list(old_list, new_list):
#         old_list = safe_list(old_list)
#         new_list = safe_list(new_list)
#         return list(set(old_list + new_list)) if new_list else old_list

#     def merge_relations(old_list, new_list):
#         old_list = safe_list(old_list)
#         new_list = safe_list(new_list)
#         merged_dict = {}

#         for rel in old_list:
#             if ':' in rel:
#                 name, relation = map(str.strip, rel.split(':', 1))
#                 merged_dict[name] = relation

#         for rel in new_list:
#             if ':' in rel:
#                 name, relation = map(str.strip, rel.split(':', 1))
#                 merged_dict[name] = relation  

#         return [f"{name}: {relation}" for name, relation in merged_dict.items()]

#     character_role_tool = CharacterRoleTool()
#     chain_input = {
#         "text": str(state['last_summary']),
#         "profiles": str([char.profile for char in state['last_profiles']])
#     }

#     chain = profile_update_prompt | profile_update_llm
#     response = chain.invoke(chain_input)
    
#     book_id = state.get('book_id')
#     character_adapter = get_character_adapter(book_id)

#     existing_by_id = {c.id: c for c in state['last_profiles']}
#     existing_by_name = {safe_str(c.profile.name).lower(): c for c in state['last_profiles']}

#     updated_characters = []

#     for new_profile_data in response.profiles:
#         new_name = safe_str(new_profile_data.name).lower()
#         new_id = getattr(new_profile_data, "id", None)

#         if new_id and new_id in existing_by_id:
#             existing_character = existing_by_id[new_id]
#         elif new_name in existing_by_name:
#             existing_character = existing_by_name[new_name]
#         else:
#             existing_character = None

#         if existing_character:
#             old_profile = existing_character.profile

#             name = safe_str(new_profile_data.name or old_profile.name)
#             age = safe_str(new_profile_data.age or old_profile.age)
#             role = safe_str(new_profile_data.role) or safe_str(old_profile.role)
#             events = merge_list(old_profile.events, new_profile_data.events)
#             relations = merge_relations(old_profile.relations, new_profile_data.relations)
#             aliases = merge_list(old_profile.aliases, new_profile_data.aliases)
#             physical_characteristics = merge_list(old_profile.physical_characteristics, new_profile_data.physical_characteristics)
#             personality = merge_list(old_profile.personality, new_profile_data.personality)

#             merged_profile = Profile(
#                 name=name,
#                 age=age,
#                 role=role,
#                 events=events,
#                 relations=relations,
#                 aliases=aliases,
#                 physical_characteristics=physical_characteristics,
#                 personality=personality
#             )

#             character_id = existing_character.id

#         else:
#             merged_profile = Profile(
#                 name=safe_str(new_profile_data.name),
#                 age=safe_str(new_profile_data.age),
#                 role=safe_str(new_profile_data.role),
#                 events=safe_list(new_profile_data.events),
#                 relations=safe_list(new_profile_data.relations),
#                 aliases=safe_list(new_profile_data.aliases),
#                 physical_characteristics=safe_list(new_profile_data.physical_characteristics),
#                 personality=safe_list(new_profile_data.personality)
#             )
#             character_id = getattr(new_profile_data, "id", None) or str(uuid.uuid4())

#         try:
#             uuid_obj = uuid.UUID(str(character_id))
#             character_id = str(uuid_obj)
#         except ValueError:
#             character_id = str(uuid.uuid4())

#         profile_dict = merged_profile.model_dump()
#         character_adapter.update_character(character_id, profile_dict)

#         updated_characters.append(Character(id=character_id, profile=merged_profile))

#     return {
#         'last_profiles': updated_characters,
#     }


def chunk_updater(state: State):
    """
    Node that updates the previous and current chunks in the state.
    """
    try:
        current_chunk = next(state['chunk_generator'])
        chunk_num = state.get('chunk_num', 0) + 1
        
        return {
            'previous_chunk': state.get('current_chunk', ''),
            'current_chunk': current_chunk,
            'chunk_num': chunk_num,
            'no_more_chunks': False
        }
    except StopIteration:
        return {'no_more_chunks': True}

    

# def summarizer(state: State):
#     """
#     Node that summarizes the text based on the profiles.
#     """
#     third_of_length_of_last_summary = len(state['last_summary']) // 3
#     context = str(state['last_summary'][2 * third_of_length_of_last_summary:]) + " " + str(state['current_chunk'])
    
#     character_names = state['last_appearing_characters']
    
#     chain_input = {
#         "text": context,
#         "names": str(character_names)
#     }
#     chain = summary_prompt | summary_llm

#     response = chain.invoke(chain_input)

#     return {"last_summary": response.summary}

def summarizer(state: State):
    """
    Node that summarizes the text based on the profiles.
    """
    try:
        third_of_length_of_last_summary = len(state['last_summary']) // 3
        context = str(state['last_summary'][2 * third_of_length_of_last_summary:]) + " " + str(state['current_chunk'])

        character_names = state['last_appearing_characters']

        chain_input = {
            "text": context,
            "names": str(character_names)
        }
        chain = summary_prompt | summary_llm
        response = chain.invoke(chain_input)

        return {
            "last_summary": response.summary,
            "summary_status": "done"   
        }

    except Exception:
        return {
            "last_summary": state.get("last_summary", ""), 
            "summary_status": "next_chunk"   
        }


def text_quality_assessor(state):
    """
    Node that assesses the quality of Arabic text using Gemini AI.
    """
    formatted_chunks = get_validation_chunks(state['file_path'],  chunk_size=30, num_chunks_to_select=5)
    
    chain_input = {
        "text": formatted_chunks
    }
    
    chain = text_quality_assessment_prompt | text_quality_assessment_llm
    response = chain.invoke(chain_input)
    
    assessment = TextQualityAssessment(
        quality_score=response.quality_score,
        quality_level=response.quality_level,
        issues=response.issues,
        suggestions=response.suggestions,
        reasoning=response.reasoning
    )
    
    return {
        'text_quality_assessment': assessment
    }


def text_classifier(state: State):
    """
    Node that classifies the input text as literary or non-literary using Gemini AI.
    """
    formatted_chunks = get_validation_chunks(state['file_path'], chunk_size=30, num_chunks_to_select=5)
    
    chain_input = {
        "text": formatted_chunks
    }
    
    chain = text_classification_prompt | text_classification_llm
    response = chain.invoke(chain_input)
    
    classification = TextClassification(
        is_literary=response.is_literary,
        classification=response.classification,
        confidence=response.confidence,
        reasoning=response.reasoning,
        literary_features=response.literary_features,
        non_literary_features=response.non_literary_features
    )
    
    return {
        'text_classification': classification
    }



def empty_profile_validator(state: State):
    """
    Node that validates Empty profiles and Suggest Changes.
    """
    chain_input = {
        "text": str(state['last_summary']),
        "profiles": str([char.profile for char in state['last_profiles']])
    }
    
    chain = empty_profile_validation_prompt | empty_profile_validation_llm
    
    response = chain.invoke(chain_input)
    
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
