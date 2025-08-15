from ai_workflow.src.language_models.prompts import name_query_prompt, profile_update_prompt, summary_prompt, text_quality_assessment_prompt, text_classification_prompt, empty_profile_validation_prompt
from ai_workflow.src.language_models.llms import name_query_llm, profile_update_llm, summary_llm, text_quality_assessment_llm, text_classification_llm, empty_profile_validation_llm
from ai_workflow.src.preprocessors.text_checkers import ArabicLanguageDetector
from ai_workflow.src.schemas.states import State
from ai_workflow.src.preprocessors.text_splitters import TextChunker
from ai_workflow.src.preprocessors.text_cleaners import clean_arabic_text_comprehensive
from ai_workflow.src.preprocessors.metadata_remover import remove_book_metadata
from ai_workflow.src.databases.django_adapter import get_character_adapter
from ai_workflow.src.schemas.output_structures import *
from ai_workflow.src.preprocessors.epub.epub_extractor import extract_text_from_file
import os 
from ai_workflow.src.preprocessors.text_splitters import get_validation_chunks

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
        
    chunker = TextChunker(chunk_size=5000, chunk_overlap=200)
    
    chunks = chunker.chunk_text_arabic_optimized(content_text)
    
    def chunk_generator():
        for chunk in chunks:
            yield chunk
            
    gen = chunk_generator()
        
    return {
        'chunk_generator': gen,
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


def profile_retriever_creator(state: State):
    """
    Node that creates a new profile or retrieves an existing one.
    Uses last_appearing_characters to retrieve profiles from Django Character models.
    If no character exists, creates a new entry with that name, keeping other profile data null.    
    """
    last_appearing_characters = state['last_appearing_characters']
    book_id = state.get('book_id')
    
    # Get the Django character adapter with book context
    character_adapter = get_character_adapter(book_id)
    
    characters = []
    
    for character_name in last_appearing_characters:
        
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
    chain = profile_update_prompt | profile_update_llm
    response = chain.invoke(chain_input)
    
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
    try:
        current_chunk = next(state['chunk_generator'])
        return {
            'previous_chunk': state.get('current_chunk', ''),
            'current_chunk': current_chunk,
            'no_more_chunks': False
        }
    except StopIteration:
        return {'no_more_chunks': True}

    

def summarizer(state: State):
    """
    Node that summarizes the text based on the profiles.
    """
    third_of_length_of_last_summary = len(state['last_summary'])//3
    context = str(state['last_summary'][2 * third_of_length_of_last_summary:]) + " " + str(state['current_chunk'])
    
    character_names = state['last_appearing_characters']
    
    chain_input = {
        "text": context,
        "names": str(character_names)
    }
    chain = summary_prompt | summary_llm
    response = chain.invoke(chain_input)
    
    return {'last_summary': response.summary}


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
