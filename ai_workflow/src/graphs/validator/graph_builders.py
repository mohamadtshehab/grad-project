from langgraph.graph import StateGraph, START, END
from ai_workflow.src.schemas.states import State
from ai_workflow.src.graphs.validator.regular_nodes import *
from ai_workflow.src.graphs.validator.router_nodes import *
graph = StateGraph(State)

graph.add_node("language_checker",language_checker)
graph.add_node('text_quality_assessor', text_quality_assessor)
graph.add_node('text_classifier', text_classifier)


graph.set_entry_point('language_checker')

graph.add_conditional_edges('language_checker', router_from_language_checker_to_text_quality_assessor_or_end, {
    'text_quality_assessor': 'text_quality_assessor',
    'END': END
})

graph.add_conditional_edges('text_quality_assessor', router_from_text_quality_assessor_to_text_classifier_or_end, {
    'text_classifier': 'text_classifier',
    'END': END
})

graph.add_edge('text_classifier', END)


validator_graph = graph.compile()
