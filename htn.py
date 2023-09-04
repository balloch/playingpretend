class HTNPlanner:
    def __init__(self):
        self.tasks = {}
        self.methods = {}

    def add_task(self, task_name, primitive_task):
        self.tasks[task_name] = primitive_task

    def add_method(self, task_name, method):
        self.methods[task_name] = method

    def execute_primitive_task(self, task):
        print(f"Executing primitive task: {task}")

    def apply_method(self, task, state):
        if task in self.tasks:
            self.execute_primitive_task(self.tasks[task])
        elif task in self.methods:
            subtasks = self.methods[task](state)
            for subtask in subtasks:
                self.apply_task(subtask, state)

    def apply_task(self, task, state):
        if isinstance(task, str):
            self.apply_method(task, state)
        elif isinstance(task, list):
            for subtask in task:
                self.apply_task(subtask, state)

def primitive_task_a():
    print("Performing primitive task A")

def primitive_task_b():
    print("Performing primitive task B")

def method_task_x(state):
    if state.get("condition"):
        return ["primitive_task_a", "primitive_task_b"]
    return ["primitive_task_a"]

def method_task_y(_):
    return ["primitive_task_b"]

if __name__ == "__main__":
    planner = HTNPlanner()

    planner.add_task("primitive_task_a", primitive_task_a)
    planner.add_task("primitive_task_b", primitive_task_b)

    planner.add_method("method_task_x", method_task_x)
    planner.add_method("method_task_y", method_task_y)

    initial_state = {"condition": True}
    high_level_goal = ["method_task_x", "method_task_y"]

    for task in high_level_goal:
        planner.apply_task(task, initial_state)
