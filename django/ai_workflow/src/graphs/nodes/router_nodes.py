from ai_workflow.src.schemas.states import State


def router_from_text_quality_assessor_to_cleaner_or_end(state : State):
    """
    Node that routes to the cleaner or end based on the response from the text quality assessor.
    """
    if state['text_quality_assessment'].quality_score >= 0.6:
        return 'cleaner'
    else:
        return 'END'

def router_from_language_checker_to_text_quality_assessor_or_end(state : State):
    """
     Node that routes to the text quality assessor or end based on the response from the language checker.
    """
    if state["is_arabic"]:
        return "text_quality_assessor"
    else:
        return "END"
    
    
def router_from_chunker_to_first_name_querier_or_end(state: State):
    """
    Node that routes to the name querier or end based on the response from the chunker.
    """
    if state['no_more_chunks']:
        return 'END'
    else:
        return 'first_name_querier'
    
    
def router_from_first_name_querier_to_summarizer_or_chunk_updater(state: State):
    """
    Node that routes to the summarizer or chunk updater based on the response from the first name querier.
    """
    if state['last_appearing_characters']:
        return 'summarizer'
    else:
        return 'chunk_updater'

def router_from_text_quality_assessor_to_text_classifier_or_end(state: State):
    """
    Node that routes to the text classifier or end based on the response from the text quality assessor.
    """
    if state['text_quality_assessment'].quality_score >= 0.6:
        return 'text_classifier'
    else:
        return 'END'

def router_from_text_classifier_to_cleaner_or_end(state: State):
    """
    Node that routes to the cleaner or end based on the response from the text classifier.
    """
    if state['text_classification'].is_literary:
        return 'cleaner'
    else:
        return 'END'

def router_from_empty_profile_validator_to_chunk_updater_or_end(state: State):
    """
    Node that routes to profile refresher or end based on profile validation results.
    """
    validation = state['empty_profile_validation']
    
    # If there are significant issues with profiles, continue to profile refresher
    if validation.validation_score < 0.5:
        return 'END'
    else:
        return 'chunk_updater'
