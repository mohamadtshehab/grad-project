from langgraph.graph import StateGraph, START, END
from ai_workflow.src.schemas.states import State
from ai_workflow.src.graphs.subgraphs.analyst.nodes.regular_nodes import *
from ai_workflow.src.graphs.subgraphs.analyst.nodes.router_nodes import *

graph = StateGraph(State)
graph.add_node('first_name_querier', first_name_querier)
graph.add_node('second_name_querier', second_name_querier)
graph.add_node('profile_retriever_creator', profile_retriever_creator)
graph.add_node('profile_refresher', profile_refresher)
graph.add_node('chunk_updater', chunk_updater)
graph.add_node('summarizer', summarizer)


graph.add_conditional_edges('chunk_updater', router_from_chunk_updater_to_first_name_querier_or_end, {
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

graph.set_entry_point('first_name_querier')

graph.add_edge('summarizer', 'second_name_querier')

graph.add_edge('second_name_querier', 'profile_retriever_creator')

graph.add_edge('profile_retriever_creator', 'profile_refresher')

graph.add_edge('profile_refresher', 'chunk_updater')


analyst_graph = graph.compile()