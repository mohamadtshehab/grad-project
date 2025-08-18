from ai_workflow.src.schemas.states import State

    
def router_from_chunk_updater_to_first_name_querier_or_end(state: State):
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
    if state['last_appearing_names']:
        return 'summarizer'
    else:
        return 'chunk_updater'



