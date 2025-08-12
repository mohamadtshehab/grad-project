from dotenv import load_dotenv
from ai_workflow.src.graphs.graph_builders import compiled_graph
from ai_workflow.src.schemas.states import initial_state
from ai_workflow.src.configs import GRAPH_CONFIG
from ai_workflow.src.graphs.graph_visualizers import visualize_graph
from ai_workflow.src.databases.database import character_db

load_dotenv()

if __name__ == "__main__":
    visualize_graph(compiled_graph)
    character_db.clear_database()
    response = compiled_graph.invoke(initial_state, config=GRAPH_CONFIG)
    print(response)