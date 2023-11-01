class Task:  # (BaseModel)
    """
    A task is a tuple t = (N, T, E, P), where N is a task name, T is a set of precodition terms.
    The precondition terms of a task are the things the must be true for the task to be performed.
    These may be simply symbols, which will be checked for existence ('John' is valid if the state contains 'John'),
    or they may be predicates, which will be checked for truth ('at(John, Home)' is valid if the state contains 'at(John, Home)').
    E are the expected effects of the task, which are checked for truth after the task is performed.
    P is the primitive function, which is null if the task is a compound task.
    When the task is called for execution, if it is primitive, it executes the primitive function P.
    If not, it iteratively calls the functions of its subtasks.
    """

    def __init__(self, name, preconditions=[], expected_start_location=None, expected_visit_location=[],
                 objects_required=[], primitive_fn=None, subtasks=[], effects=[], root=False):
        # super().__init__(**kwargs)
        self.name = name
        self.precon_terms = preconditions
        self.expected_start_location = expected_start_location
        self.expected_visit_location = expected_visit_location
        self.objects_required = objects_required
        self.primitive_fn = primitive_fn
        self.subtasks = subtasks
        self.effects = effects
        self.root = root

    def add_subtask(self, subtask):
        self.subtasks.append(subtask)

    def add_precondition(self, pre_key, pre_value):
        if pre_key in self.precon_terms:
            self.precon_terms[pre_key].append(pre_value)
        else:
            self.precon_terms[pre_key] = [pre_value]

    def __call__(self, state, **kwds):
        # If primitive, this is an operator that has some effect on the world
        # If not primitive, calls its list of subtasks
        e = ['Execution Errors:']
        if self.primitive_fn:
            expected_state = state.sim_apply_effects(self.effects)
            new_state = self.primitive_fn(state, **kwds)
            diff = new_state.diff(expected_state)
            if diff:
                return [(self.name, 'StateMatch', state, diff)]
            else:
                return []
        else:
            # call each function in a list of functions self.subtasks
            for subtask in self.subtasks:
                e.extend(subtask(state, **kwds))
        return e

    def __hash__(self):
        return hash(frozenset((self.name, self.primitive_fn)))

    def __eq__(self, other):
        return isinstance(other, Task) and self.name == other.name and self.primitive_fn == other.primitive_fn

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Task: {self.name}"
