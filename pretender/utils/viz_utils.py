from graphviz import Digraph

from pretender.htn import Task


def visualize_task_tree(root_task):
    dot = Digraph(comment="Task Tree")
    stack = [(root_task, None)]  # Use a stack for depth-first traversal

    while stack:
        task, parent_id = stack.pop()
        task_id = id(task)

        if parent_id is not None:
            dot.edge(str(parent_id), str(task_id))

        dot.node(str(task_id), task.name)

        for subtask in task.subtasks:
            stack.append((subtask, task_id))

    return dot


## Main visualization function
# Create your Task objects and define their relationships
# root_task = Task("Root Task", subtasks=[
#     Task("Subtask 1"),
#     Task("Subtask 2", subtasks=[
#         Task("Subtask 2.1"),
#         Task("Subtask 2.2"),
#     ]),
# ], root=True)

