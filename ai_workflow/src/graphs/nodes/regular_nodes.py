from ai_workflow.src.language_models.prompts import name_query_prompt, profile_update_prompt, summary_prompt, text_quality_assessment_prompt, text_classification_prompt, empty_profile_validation_prompt
from ai_workflow.src.language_models.llms import name_query_llm, profile_update_llm, summary_llm, text_quality_assessment_llm, text_classification_llm, empty_profile_validation_llm
from ai_workflow.src.preprocessors.text_checkers import ArabicLanguageDetector
from ai_workflow.src.schemas.states import State
from ai_workflow.src.preprocessors.text_splitters import TextChunker
from ai_workflow.src.preprocessors.text_cleaners import clean_arabic_text_comprehensive
from ai_workflow.src.preprocessors.metadata_remover import remove_book_metadata
from ai_workflow.src.databases.database import character_db
from ai_workflow.src.schemas.data_classes import Profile, TextQualityAssessment, TextClassification, EmptyProfileValidation
from ai_workflow.src.language_models.tools import CharacterRoleTool
from dataclasses import asdict
import os
import random

def language_checker(state : State):
    """
    Node that Checks the text from the file before cleaning.
    Uses the check_text function to make sure the input text is in Arabic.
    """
    file_path = state['file_path']
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text = file.read()
    detector = ArabicLanguageDetector()
    
    result = detector.check_text(raw_text)
    return {
        'is_arabic': result
    }
    
    
def cleaner(state: State):
    """
    Node that cleans the text from the file before chunking.
    Uses the clean_text function to normalize and clean the input text.
    """
    file_path = state['file_path']
    
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text = file.read()

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
    
    characters = response.characters if hasattr(response, 'characters') else []
    
    return {
        'last_appearing_characters': characters
    } 


def profile_retriever_creator(state: State):
    """
    Node that creates a new profile or retrieves an existing one.
    Uses last_appearing_characters to retrieve profiles from character_db. If no character exists,
    creates a new entry with that name and hint, keeping other profile data null.
    """
    last_appearing_characters = state['last_appearing_characters']
    
    profiles = []
    
    for character in last_appearing_characters:
        name = character.name
        hint = character.hint
        
        existing_characters = character_db.find_characters_by_name(name)
        
        if existing_characters:
            # create the data dictionary that will be send to the LLM
            for char in existing_characters:
                profile_data = char['profile']
                profile = Profile(
                    name=char['name'],
                    hint=profile_data['hint'],
                    age=profile_data['age'],
                    role=profile_data['role'],
                    physical_characteristics=profile_data['physical_characteristics'],
                    personality=profile_data['personality'],
                    events=profile_data['events'],
                    relations=profile_data['relations'],
                    aliases=profile_data['aliases'],
                    id=char['id']
                )
                profiles.append(profile)
        else:
            # create the json object that will be stored in the database (no need for id because it has its own column)
            new_profile = {
                'name': name,
                'hint': hint,
                'age': '',
                'role': '',
                'physical_characteristics': [],
                'personality': '',
                'events': [],
                'relations': [],
                'aliases': [],
            }
            
            # Insert character and get the generated ID
            character_id = character_db.insert_character(name, new_profile)
            
            # Create data dictionary that will be send to the LLM
            profile = Profile(
                name=name,
                hint=hint,
                age='',
                role='',
                physical_characteristics=[],
                personality='',
                events=[],
                relations=[],
                aliases=[],
                id=character_id,  # Use the generated ID from database
            )
            profiles.append(profile)
    
    return {'last_profiles': profiles}


# def profile_refresher(state: State):
#     """
#     Node that refreshes the profiles based on the current chunk.
#     """
#     chain_input = {
#         "text": str(state['last_summary']),
#         "profiles": str(state['last_profiles'])
#     }
#     chain = profile_update_prompt | profile_update_llm
#     response = chain.invoke(chain_input)
    
#     # Extract profiles from the structured output
#     updated_profiles = []
#     for profile_data in response.profiles:
#         # create the data dictionary that will be an item in the list of profiles in the state
#         profile = Profile(
#             name=profile_data.name,
#             hint=profile_data.hint,
#             age=profile_data.age,
#             role=profile_data.role,  # Use the role determined by the LLM with tool
#             physical_characteristics=profile_data.physical_characteristics,
#             personality=profile_data.personality,
#             events=profile_data.events,
#             relations=profile_data.relations,
#             aliases=profile_data.aliases,
#             id=profile_data.id
#         )
#         updated_profiles.append(profile)
        
#         # create the json object that will be updated in the database
#         updated_profile_dict = {
#             'name': profile_data.name,
#             'hint': profile_data.hint,
#             'age': profile_data.age,
#             'role': profile_data.role,  # Use the role determined by the LLM with tool
#             'physical_characteristics': profile_data.physical_characteristics,
#             'personality': profile_data.personality,
#             'events': profile_data.events,
#             'relations': profile_data.relations,
#             'aliases': profile_data.aliases,
#         }
    
#         # Only update if the profile has a valid ID
#         if profile_data.id:
#             character_db.update_character(
#                 profile_data.id,
#                 updated_profile_dict
#             )
    
#     return {
#         'last_profiles': updated_profiles,
#     }

def profile_refresher(state: State):
    """
    Refreshes profiles based on the current chunk.
    Merges updates returned by the LLM with existing profiles.
    Ensures no None/null values in output.
    Relations are merged intelligently: last relation for each character is kept.
    """

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
        merged_dict = {}

        for rel in old_list:
            if ':' in rel:
                name, relation = map(str.strip, rel.split(':', 1))
                merged_dict[name] = relation

        for rel in new_list:
            if ':' in rel:
                name, relation = map(str.strip, rel.split(':', 1))
                merged_dict[name] = relation  

        return [f"{name}: {relation}" for name, relation in merged_dict.items()]

    character_role_tool = CharacterRoleTool()
    chain_input = {
        "text": str(state['last_summary']),
        "profiles": str(state['last_profiles'])
    }

    chain = profile_update_prompt | profile_update_llm
    response = chain.invoke(chain_input)

    updated_profiles = []
    old_by_id = {p.id: p for p in state['last_profiles']}

    for new_profile_data in response.profiles:
        old_profile = old_by_id.get(new_profile_data.id)

        if old_profile:
            name = safe_str(new_profile_data.name or old_profile.name)
            hint = safe_str(new_profile_data.hint or old_profile.hint)
            age = safe_str(new_profile_data.age or old_profile.age)
            role = safe_str(new_profile_data.role) or safe_str(old_profile.role)

            events = merge_list(old_profile.events, new_profile_data.events)
            relations = merge_relations(old_profile.relations, new_profile_data.relations)
            aliases = merge_list(old_profile.aliases, new_profile_data.aliases)
            physical_characteristics = merge_list(old_profile.physical_characteristics, new_profile_data.physical_characteristics)
            personality = merge_list(old_profile.personality, new_profile_data.personality)

            merged_profile = Profile(
                id=safe_str(old_profile.id),
                name=name,
                hint=hint,
                age=age,
                role=role,
                events=events,
                relations=relations,
                aliases=aliases,
                physical_characteristics=physical_characteristics,
                personality=personality
            )
        else:
            role_value = safe_str(new_profile_data.role)
            if not role_value:
                role_value = safe_str(character_role_tool.run({
                    "character_description": new_profile_data.hint or "",
                    "personality": ", ".join(safe_list(new_profile_data.personality)),
                    "events": ", ".join(safe_list(new_profile_data.events)),
                    "relationships": ", ".join(safe_list(new_profile_data.relations))
                }))

            merged_profile = Profile(
                id=safe_str(new_profile_data.id),
                name=safe_str(new_profile_data.name),
                hint=safe_str(new_profile_data.hint),
                age=safe_str(new_profile_data.age),
                role=role_value,
                events=safe_list(new_profile_data.events),
                relations=safe_list(new_profile_data.relations),
                aliases=safe_list(new_profile_data.aliases),
                physical_characteristics=safe_list(new_profile_data.physical_characteristics),
                personality=safe_list(new_profile_data.personality)
            )

        updated_profiles.append(merged_profile)
        updated_profile_dict = asdict(merged_profile)
        if merged_profile.id:
            character_db.update_character(merged_profile.id, updated_profile_dict)

    return {'last_profiles': updated_profiles}

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

    

def summarizer(state: State):
    """
    Node that summarizes the text based on the profiles.
    """
    third_of_length_of_last_summary = len(state['last_summary']) // 3
    context = str(state['last_summary'][2 * third_of_length_of_last_summary:]) + " " + str(state['current_chunk'])
    chain_input = {
        "text": context,
        "names": str(state['last_appearing_characters'])
    }
    chain = summary_prompt | summary_llm

    response = chain.invoke(chain_input)

    if not response or not hasattr(response, "summary") or response.summary is None:
        response = chain.invoke(chain_input)

    return {"last_summary": response.summary}

def text_quality_assessor(state):
    """
    Node that assesses the quality of Arabic text using Gemini AI.
    """
    file_path = state['file_path']
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text_lines = file.readlines()
    
    def get_non_overlapping_chunks(lines, num_lines_per_chunk):
        """
        Splits a list of lines into non-overlapping chunks.
        """
        chunks = []
        for i in range(0, len(lines), num_lines_per_chunk):
            chunk = "".join(lines[i:i + num_lines_per_chunk])
            chunks.append(chunk)
        return chunks

    all_chunks = get_non_overlapping_chunks(raw_text_lines, 10) # 20 lines per chunk
    
    # Select 10 random, non-overlapping chunks
    num_chunks_to_select = 3
    if len(all_chunks) > num_chunks_to_select:
        random_chunks = random.sample(all_chunks, num_chunks_to_select)
    else:
        random_chunks = all_chunks

    # Format the selected chunks for the LLM
    formatted_chunks = ""
    for i, chunk in enumerate(random_chunks):
        formatted_chunks += f"Chunk {i+1}:\n{chunk}\n"

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
    file_path = state['file_path']
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text = file.read()
    
    # Split the raw text into a list of words.
    words = raw_text.split()
    
    def get_non_overlapping_word_chunks(all_words, num_words_per_chunk):
        """
        Splits a list of words into non-overlapping chunks.
        """
        chunks = []
        for i in range(0, len(all_words), num_words_per_chunk):
            chunk_words = all_words[i:i + num_words_per_chunk]
            chunk = " ".join(chunk_words) # Join the words back into a single string
            chunks.append(chunk)
        return chunks

    # You can adjust this number to set the desired chunk size in words.
    num_words_per_chunk = 15
    
    all_chunks = get_non_overlapping_word_chunks(words, num_words_per_chunk)
    
    # Select 10 random, non-overlapping chunks
    num_chunks_to_select = 10
    if len(all_chunks) > num_chunks_to_select:
        random_chunks = random.sample(all_chunks, num_chunks_to_select)
    else:
        random_chunks = all_chunks

    # Format the selected chunks for the LLM
    formatted_chunks = ""
    for i, chunk in enumerate(random_chunks):
        formatted_chunks += f"Chunk {i+1}:\n{chunk}\n"

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
    if not state['last_profiles']:
        return {
            'empty_profile_validation': EmptyProfileValidation(
                has_empty_profiles=False,
                empty_profiles=[],
                suggestions=["لا توجد بروفايلات للتحقق منها"],
                profiles=[],
                validation_score=1.0
            )
        }
    
    # Convert profiles to a format suitable for the LLM
    profiles_text = ""
    for i, profile in enumerate(state['last_profiles']):
        profiles_text += f"البروفايل {i+1}:\n"
        profiles_text += f"الاسم: {profile.name}\n"
        profiles_text += f"التلميح: {profile.hint}\n"
        profiles_text += f"العمر: {profile.age}\n"
        profiles_text += f"الدور: {profile.role}\n"
        profiles_text += f"الصفات الجسدية: {', '.join(profile.physical_characteristics)}\n"
        profiles_text += f"الشخصية: {profile.personality}\n"
        profiles_text += f"الأحداث: {', '.join(profile.events)}\n"
        profiles_text += f"العلاقات: {', '.join(profile.relations)}\n"
        profiles_text += f"الأسماء البديلة: {', '.join(profile.aliases)}\n"
        profiles_text += "---\n"
    
    chain_input = {
        "text": str(state['last_summary']),
        "profiles": profiles_text
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
    updated_profiles = []
    for profile_data in response.profiles:
        # create the data dictionary that will be an item in the list of profiles in the state
        profile = Profile(
            name=profile_data.name,
            hint=profile_data.hint,
            age=profile_data.age,
            role=profile_data.role,  # Use the role determined by the LLM with tool
            physical_characteristics=profile_data.physical_characteristics,
            personality=profile_data.personality,
            events=profile_data.events,
            relations=profile_data.relations,
            aliases=profile_data.aliases,
            id=profile_data.id
        )
        updated_profiles.append(profile)
        
        # create the json object that will be updated in the database
        updated_profile_dict = {
            'name': profile_data.name,
            'hint': profile_data.hint,
            'age': profile_data.age,
            'role': profile_data.role,  # Use the role determined by the LLM with tool
            'physical_characteristics': profile_data.physical_characteristics,
            'personality': profile_data.personality,
            'events': profile_data.events,
            'relations': profile_data.relations,
            'aliases': profile_data.aliases,
        }
    
        # Only update if the profile has a valid ID
        if profile_data.id:
            character_db.update_character(
                profile_data.id,
                updated_profile_dict
            )
    return {
        'empty_profile_validation': empty_profile_validation,
        'last_profiles': updated_profiles  # Also update last_profiles with the validated profiles
    }
