from ai_workflow.src.schemas.states import State

def router_from_validator_to_name_extractor_or_end(state: State):
    """
    Node that routes to the name extractor or end based on the response from the validator.
    """
    
    if state['validation_passed']:
        return 'name_extractor'
    else:
        return 'END'