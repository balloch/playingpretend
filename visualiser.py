from pretender.utils.viz_utils import visualize_task_tree
import pickle

with open('story_tree_intermediate.pkl', 'rb') as f:
    story_tree = pickle.load(f)

dot_graph = visualize_task_tree(story_tree, end_early=True)  # root_task)

# Render the graph as an image in the notebook
dot_graph.format = 'png'
dot_graph.render("task_tree", view=True)