from langgraph.graph import StateGraph, START, END
from ai_workflow.src.schemas.states import State
from ai_workflow.src.graphs.subgraphs.validator.graph_builders import validator_graph
from ai_workflow.src.graphs.subgraphs.preprocessor.graph_builders import preprocessor_graph
from ai_workflow.src.graphs.subgraphs.analyst.graph_builders import analyst_graph
from ai_workflow.src.graphs.orhcestrator.nodes.router_nodes import router_from_validator_to_name_extractor_or_end
from ai_workflow.src.graphs.orhcestrator.nodes.regular_nodes import name_extractor

graph = StateGraph(State)

graph.add_node("validator",validator_graph)
graph.add_node("preprocessor",preprocessor_graph)
graph.add_node("analyst",analyst_graph)
graph.add_node("name_extractor",name_extractor)


graph.set_entry_point('validator')

graph.add_conditional_edges('validator', router_from_validator_to_name_extractor_or_end, {
    'name_extractor': 'name_extractor',
    'END': END
})

graph.add_edge('name_extractor', 'preprocessor')
graph.add_edge('preprocessor', 'analyst')


orchestrator_graph = graph.compile()