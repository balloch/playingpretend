import copy

from common.AtomicAction import AtomicAction

class Task:  # (BaseModel)
    """
    A task is a tuple t = (N, T, E, P), where N is a task id, T is a set of precodition terms.
    The precondition terms of a task are the things the must be true for the task to be performed.
    These may be simply symbols, which will be checked for existence ('John' is valid if the state contains 'John'),
    or they may be predicates, which will be checked for truth ('at(John, Home)' is valid if the state contains 'at(John, Home)').
    E are the expected effects of the task, which are checked for truth after the task is performed.
    P is the primitive function, which is null if the task is a compound task.
    When the task is called for execution, if it is primitive, it executes the primitive function P.
    If not, it iteratively calls the functions of its subtasks.
    """

    def __init__(self, name, preconditions=[[], []], variables=None, expected_start_location=None,
                 expected_visit_location=[],
                 objects_required=[], primitive_fn=None, primitive_const={}, subtasks=[], effects=[], root=False,
                 goal=False):
        # super().__init__(**kwargs)
        self.name = name
        self.preconditions = preconditions
        self.effects = effects
        if variables is None:
            variables = []
        self.variables = variables  ## list of unique strings
        self.assignments = {}  ## dictionary of values assigned to those strings
        for var in self.variables:
            self.assignments[var] = ''
        self.subtasks = subtasks
        self.expected_start_location = expected_start_location
        self.expected_visit_location = expected_visit_location
        self.objects_required = objects_required
        self.primitive_fn = primitive_fn
        self.primitive_const = primitive_const
        if self.primitive_fn:
            self.satisfied = True
        else:
            self.satisfied = False
        self.root = root
        self.goal = goal
        self.execution_state = 0

    def add_subtask(self, subtask):
        self.subtasks.append(subtask)

    def add_precondition(self, pre_key, pre_value):
        if pre_key in self.preconditions:
            self.preconditions[pre_key].append(pre_value)
        else:
            self.preconditions[pre_key] = [pre_value]

    def from_atomic(self, atomic, function=None):
        blacklist = ['inreceptacle', 'receptacletype', 'cancontain', 'objecttype']
        ## abs types: '?r', '?a', '?lend'
        # TODO this should just use the Precondition and Effects classes
        # TODO: refactor below so that there is less code reuse
        precons_pos = []
        for precon in atomic.preconditions:
            if precon.name in blacklist:
                continue  # Skipping. See TODOs in client_example.py:process_init()
            precon_pos = [precon.name]
            for p in precon.parameters:
                p_name = p.name
                ## below commented out because seems not necessary
                # p_name = p.name+'1'
                # val = 1
                # while p_name in self.variables:
                #     val += 1
                #     p_name[:-1]+str(val)
                self.variables.append(p_name)
                precon_pos.append('{'+p_name+'}')
            precons_pos.append(tuple(precon_pos))
        # TODO: add negative when added to the precondition class
        precons_neg = []
        self.preconditions = [precons_pos, precons_neg]

        effects_pos = []  # added effects
        for effect in atomic.add_effects:
            if effect.name in blacklist:
                continue  # Skipping. See TODOs in client_example.py:process_init()
            eff_pos = [effect.name]
            for p in effect.parameters:
                p_name = p.name
                self.variables.append(p_name)
                eff_pos.append('{'+p_name+'}')
            effects_pos.append(tuple(eff_pos))
        effects_neg = []  # removed effects
        for effect in atomic.del_effects:
            if effect.name in blacklist:
                continue  # Skipping. See TODOs in client_example.py:process_init()
            eff_neg = [effect.name]
            for p in effect.parameters:
                p_name = p.name
                self.variables.append(p_name)
                eff_neg.append('{'+p_name+'}')
            effects_neg.append(tuple(eff_neg))
        self.effects = [effects_pos, effects_neg]

        self.variables = list(set(self.variables))
        for var in self.variables:
            self.assignments[var] = ''


        self.primitive_fn = function
        # TODO: remove the need for this hardcoding
        if atomic.command_template == 'go to {l}':
            atomic.command_template = 'go to {?r}'
        if atomic.command_template == 'take {o} from {r}':
            atomic.command_template = 'take {?o} from {?r}'
        if atomic.command_template == 'put {o} in/on {r}':
            atomic.command_template = 'put {?o} in/on {?r}'

        self.primitive_const = {'command': atomic.command_template}


    def bind_variables(self, binding):
        # TODO : this should be a property/function of predicate class
        if not (set(binding.keys()) == set(self.variables)):
            error = f'Error, not all values provided. No assignment done. \n Must provide all of the following: {self.variables}'
            print(error)
            return error
        self.assignments = binding
        self.name = self.name[:-4]
        for key, value in self.assignments.items():
            self.name += '_' + value
        ## Update the preconditions and effects
        new_precons = [[], []]
        new_effects = [[], []]
        for i in range(2):
            for precon in self.preconditions[i]:
                new_precon = [precon[0]]
                for elem in precon[1:]:
                    new_precon.append(elem.format(**self.assignments))
                new_precons[i].append(tuple(new_precon))
            for effect in self.effects[i]:
                new_effect = [effect[0]]
                for elem in effect[1:]:
                    new_effect.append(elem.format(**self.assignments))
                new_effects[i].append(tuple(new_effect))
        self.preconditions = new_precons
        self.effects = new_effects
        for key in self.primitive_const.keys():
            self.primitive_const[key] = self.primitive_const[key].format(**self.assignments)


    def check_precons(self, state):
        errors = [[pos for pos in self.preconditions[0] if pos not in state], [neg for neg in self.preconditions[1] if neg in state]]
        return errors

    def sim_apply_effects(self, state, state_change=None, nav_locations=None, warnings=False):
        new_state = copy.deepcopy(state)
        new_state, errors = self.apply_effects(new_state, state_change, nav_locations, warnings)
        return new_state, errors

    def apply_effects(self, state, state_change=None, nav_locations=None, warnings=True):
        errors = [[], []]
        for e_add in self.effects[0]:
            if e_add in state:
                errors[0].append(f"Warning: {e_add} already true")
                if warnings:
                    print(f"Warning: {e_add} already true")
            else:
                state.add(e_add)
        for e_rm in self.effects[1]:
            try:
                state.remove(e_rm)
            except KeyError:
                errors[1].append(f"Warning: {e_rm} already not present")
                if warnings:
                    print(f"Warning: {e_rm} already not present")
        return state, errors

    def check_effects(self, state, state_change=None, nav_locations=None):
        errors = [[ad for ad in self.effects[0] if ad not in state], [rm for rm in self.effects[1] if rm in state]]
        return errors

    def get_next_prim(self):
        if self.primitive_fn:
            return self
        else:  ## execute NEXT executable function
            return self.subtasks[self.execution_state]

    def execute_next(self, state, **kwds):
        kwds.update(self.primitive_const)
        if self.primitive_fn:
            response = self.primitive_fn(**kwds)
            return response
        else:  ## execute NEXT executable function
            subtask = self.subtasks[self.execution_state]
            # Move execution state if the subtask is primitive or has only one subtask remaining
            if subtask.primitive_fn:
                self.execution_state += 1
            elif len(subtask.subtasks) - 1 == subtask.execution_state + 1:
                self.execution_state += 1
            return subtask.execute_next(state, **kwds)
            # e.extend(subtask(state, **kwds))

    def __call__(self, state, **kwds):
        # If primitive, this is an operator that has some effect on the world
        # If not primitive, calls its list of subtasks
        e = ['Execution Errors:']
        if self.primitive_fn:
            response = self.primitive_fn(**kwds)
            return response
        else:  ## execute NEXT executable function
            subtask = self.subtasks[self.execution_state]
            # Move execution state if the subtask is primitive or has only one subtask remaining
            if subtask.primitive_fn:
                self.execution_state += 1
            elif len(subtask.subtasks) - 1 == subtask.execution_state + 1:
                self.execution_state += 1
            return subtask(state, kwds)

    def __hash__(self):
        return hash(frozenset((self.name, self.primitive_fn)))

    def __eq__(self, other):
        return isinstance(other, Task) and self.name == other.name and self.primitive_fn == other.primitive_fn

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Task: {self.name}"
