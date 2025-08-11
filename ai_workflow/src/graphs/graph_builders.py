from langgraph.graph import StateGraph, START, END
from ai_workflow.src.schemas.states import State
from ai_workflow.src.graphs.nodes.regular_nodes import *
from ai_workflow.src.graphs.nodes.router_nodes import *

graph = StateGraph(State)
graph.add_node("language_checker",language_checker)
graph.add_node('cleaner', cleaner)
graph.add_node('chunker', chunker)
graph.add_node('first_name_querier', first_name_querier)
graph.add_node('second_name_querier', second_name_querier)
graph.add_node('profile_retriever_creator', profile_retriever_creator)
graph.add_node('profile_refresher', profile_refresher)
graph.add_node('chunk_updater', chunk_updater)
graph.add_node('summarizer', summarizer)
graph.add_node('metadata_remover', metadata_remover)
graph.add_node('text_quality_assessor', text_quality_assessor)
graph.add_node('text_classifier', text_classifier)

graph.add_node('empty_profile_validator', empty_profile_validator)


graph.set_entry_point('language_checker')
graph.add_edge('cleaner', 'metadata_remover')
graph.add_edge('metadata_remover', 'chunker')
graph.add_edge('chunker', 'chunk_updater')

graph.add_conditional_edges(
    'empty_profile_validator',
    router_from_empty_profile_validator_to_chunk_updater_or_end,
    {
        'chunk_updater': 'chunk_updater',
        'END': END
    }
)

graph.add_conditional_edges('language_checker', router_from_language_checker_to_text_quality_assessor_or_end, {
    'text_quality_assessor': 'text_quality_assessor',
    'END': END
})

graph.add_conditional_edges('text_quality_assessor', router_from_text_quality_assessor_to_text_classifier_or_end, {
    'text_classifier': 'text_classifier',
    'END': END
})

graph.add_conditional_edges('text_classifier', router_from_text_classifier_to_cleaner_or_end, {
    'cleaner': 'cleaner',
    'END': END
})

graph.add_conditional_edges('chunk_updater', router_from_chunker_to_first_name_querier_or_end, {
    'first_name_querier': 'first_name_querier',
    'END': END
})

graph.add_conditional_edges(
    'first_name_querier',
    router_from_first_name_querier_to_summarizer_or_chunk_updater,
    {
        'summarizer': 'summarizer',
        'chunk_updater': 'chunk_updater',
    }
)


graph.add_edge('summarizer', 'second_name_querier')

graph.add_edge('second_name_querier', 'profile_retriever_creator')

graph.add_edge('profile_retriever_creator', 'profile_refresher')

graph.add_edge('profile_refresher', 'empty_profile_validator')

compiled_graph = graph.compile()