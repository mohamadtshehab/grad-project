from langgraph.graph import StateGraph, START, END
from ai_workflow.src.schemas.states import State
from ai_workflow.src.graphs.preprocessor.regular_nodes import *
from ai_workflow.src.graphs.preprocessor.router_nodes import *
from ai_workflow.src.schemas.contexts import Context

graph = StateGraph(State)
graph.add_node('cleaner', cleaner)
graph.add_node('chunker', chunker)
graph.add_node('metadata_remover', metadata_remover)

graph.set_entry_point('chunker')
graph.add_edge('chunker', 'cleaner')
graph.add_edge('cleaner', 'metadata_remover')

preprocessor_graph = graph.compile()