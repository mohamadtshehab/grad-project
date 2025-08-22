from IPython.display import Image, display

def visualize_graph(compiled_graph, name):
        mermaid_png = compiled_graph.get_graph().draw_mermaid_png()
        display(Image(mermaid_png))
        with open(f'ai_workflow/resources/images/{name}.png', 'wb') as f:
            f.write(mermaid_png)
        print(f"(🎨) Graph saved to {name}.png")