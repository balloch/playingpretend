from copy import deepcopy
from typing import List,Any
from pydantic import BaseModel, Field
import heapq
import itertools
import functools
from functools import total_ordering

class Object: #(BaseModel)
    object_coll = {}
    def __init__(self, name, loc):
        self.name = name
        self.init_loc = loc
        iter = self._put(loc)
        self.init_iter = iter

    def _put(self, new_loc):
        if (self.name, new_loc) in self.object_coll:
            self.object_coll[(self.name,new_loc)].append(self)
        else:
            self.object_coll[(self.name,new_loc)]=[self]
        self.loc = new_loc
        len(self.object_coll[(self.name,new_loc)])
        self.iter = iter
        return iter

    def move(self, new_loc):
        self.object_coll[(self.name,self.loc)].remove[self.iter]
        self._put(new_loc)

    def __hash__(self):
        return hash(frozenset((self.name, self.init_loc, self.init_iter)))

    def __eq__(self, other):
        return isinstance(other, Object) and self.name == other.name and self.init_loc == other.loc and self.init_iter == other.init_iter

    def __ne__(self, other):
        return not self.__eq__(other)


class State: #(BaseModel)
    """
    A state is a set of predicates that are true in the world.
    """
    def __init__(self, vars): #predicates):
        self.vars = vars

        # super().__init__(**kwargs)
        # self.predicates = predicates

    def apply_effects(self, predicate_list):
        pass
        # for predicate in predicate_list:
        #     if predicate not in self.predicates:
        #         self.add_predicate(predicate)
        #     if 
        #         self.add_predicate(predicate_function[1])
        #     self.predicates.append(predicate)

    def sim_apply_effects(self, predicate_list):
        pass
        # new_state = State(self.predicates)
        # for predicate in predicate_list:
        #     if predicate not in new_state.predicates:
        #         new_state.add_predicate(predicate)
        # return new_state

    def add_predicate(self, predicate):
        self.predicates.append(predicate)

    def delete_predicate(self, predicate):
        self.predicates.append(predicate)

    def diff(self, other_state):
        # returns the predicates that are true in self but not in other_state
        return [x for x in self.predicates if x not in other_state.predicates]

    def __repr__(self):
        return f"State: {self.predicates}"


class Task: #(BaseModel)
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
    def __init__(self, description, name=None, preconditions=None, expected_start_location=None, expected_visit_location=[], objects_required=[], primitive_fn=None, subtasks=[], effects=[], root=False):
        # super().__init__(**kwargs)
        self.description = description
        self.name = name
        if preconditions is None:
            preconditions = dict()
        self.preconditions = preconditions
        self.expected_start_location = expected_start_location
        self.expected_visit_location = expected_visit_location
        self.objects_required = objects_required
        self.primitive_fn = primitive_fn
        self.subtasks = subtasks
        self.effects = effects
        self.root = root
        self.visited_planner = False

    def add_subtask(self, subtask):
        self.subtasks.append(subtask)
    
    def add_precondition(self, pre_key, pre_value):
        if pre_key in self.preconditions:
            self.preconditions[pre_key].append(pre_value)
        else:
            self.preconditions[pre_key] = [pre_value]

    def check_complete(self):
        if self.primitive_fn:
            return True
        else:
            return all(subtask.check_complete() for subtask in self.subtasks)

    def __call__(self, state, **kwds: Any) -> Any:
        # If primitive, this is an operator that has some effect on the world
        # If not primitive, calls its list of subtasks
        # e = ['Execution Errors:']
        e = None
        # Check preconditions for existence in the state
        for pre_key, pre_value in self.preconditions.items():
            if pre_key not in state.vars:
                e = [(self.name, 'PreconditionNotPresent', pre_key, pre_value)]
                return e
            elif pre_value != state.vars[pre_key]:
                e = [(self.name, 'PreconditionNotEqual', pre_key, pre_value)]
                return e
            
        if self.primitive_fn:
            expected_state = state.sim_apply_effects(self.effects)
            new_state = self.primitive_fn(state, **kwds)
            diff = new_state.diff(expected_state)
            if diff :
                return [(self.name, 'StateMatchFailure', state, diff)]
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
    


class DecompMethod: #(BaseModel)
# A decomposition method is a triple m = (NT, DEC, P), where NT is a non-primitive task, DEC is a totally-ordered list of tasks called a decomposition of NT,
# and P (the set of preconditions) is a boolean formula of first-order predicate calculus.

    def __init__(self, name, subtasks=[], preconditions=[]):
        # super().__init__(**kwargs)
        self.name = name
        self.subtasks = subtasks
        self.preconditions = preconditions

    def add_subtask(self, subtask):
        self.subtasks.append(subtask)

    def add_precondition(self, precondition):
        self.preconditions.append(precondition)

    def __call__(self, task: Task) -> Task:
        # calling a Method on a Task object will decompose the task into a list of subtasks, which are then written to the Task object's subtasks list
        # and then the Task object is returned

        # Search for decomposition of task
        soln_graph = [(0, task.terms, task)]
        # boundary is a heap of tuples (priority, task_terms, parent_task)
        # where priority is the number of tasks so far used
        # we are trying to come up with the shortest subtask lists that decompose a task

        while soln_graph:
            priority, terms, parent_task = heapq.heappop(soln_graph)
            if terms == [] and priority == 0:
                f"Could not decompose with Method {self.name}"
                return parent_task
            else:
                for subtask in self.subtasks:
                    if(all(x in terms for x in subtask.terms)):
                        heapq.heappush(soln_graph, (priority+1, task.terms, task))
        soln_path_next = soln_graph[0]
        while soln_path_next[0] > 0:
            task.add_subtask(subtask)
        # for subtask in self.subtasks:
        #     if(all(x in subtask.terms for x in task.terms)):
        #         task.add_subtask(subtask)

    def __repr__(self):
        return f"Method: {self.name}"
    


# One of the methods we construct needs to check "implies". So for example:
# State = "The robot is in the living room with John"
# Q: Does the State imply that John is home?"



class HTNPlanner: #(BaseModel)
    def __init__(self, tasks=None):
        # super().__init__(**kwargs)
        if tasks is None:
            self.tasks = {}
        else:
            self.tasks = tasks
        self.methods = {}

        # self.opened = None
        # self.closed = None


    def add_task(self, task_name, primitive_task):
        self.tasks[task_name] = primitive_task

    def add_method(self, task_name, method):
        self.methods[task_name] = method

    def execute_primitive_task(self, task):
        print(f"Executing primitive task: {task}")

    def plan(self, goal_root, initial_state=None, bindings=None):
        print('Planning...')
        self.bindings = bindings
        self._decompose(compound_task=goal_root, init_state=initial_state)
        # for i, ts in enumerate(task_spec):
        #     new_task = deepcopy(real_tasks[ts[0]])
        #     new_task.bind_variables(ts[1])
        #     goal_root.add_subtask(new_task)
        # goal_root.subtasks[-1].goal = True
        print('Done!')
        return goal_root

    @functools.total_ordering
    def _decompose(self, compound_task, init_state):
        """
        decompose the bound compound_task by A*, memoize visitations if possible.
        each entry is a tuple of (value, astar_node)
        **note: there probably should be a flag to search greedily or optimally
        """

        # TODO this should be in some utils somewhere
        class astar_node:
            def __init__(self, post_bound_state, curr_task, parent_node,dist):
                self.post_bound_state = post_bound_state
                self.curr_task = curr_task
                self.parent_node = parent_node
                if parent_node is None:
                    len_parent = 0
                elif isinstance(parent_node,astar_node):
                    len_parent = self.parent_node.dist
                else:
                    len_parent = len(self.parent_node)
                self.total_len = len(self.post_bound_state) * len_parent + 1
                self.dist = dist

            def __eq__(self, other):
                assert isinstance(other, astar_node)
                return other.post_bound_state == self.post_bound_state and other.curr_task == self.curr_task and other.parent_node == self.parent_node

            def __lt__(self, other):
                assert isinstance(other, astar_node)
                return self.total_len < other.total_len


        # goal_state = compound_task.apply_effects(init_state)
        goal_effects = compound_task.effects
        goal_reached = False
        closed = []
        closed_states = set()
        opened = [(0, astar_node(init_state, None, None, dist=0))]
        no_add_flag = False
        remove_o_idx_flag = -1
        variable_mismatch_flag = False

        test_step=0

        ##### Heuristics
        # TODO: make this a function of config
        # zero heuristic == Djykstra
        # heuristic = lambda x: 0
        # base heuristic == full precon edit distance
        heuristic = lambda x: len(compound_task.check_effects(x)[0])
        # preferred heuristic == precon parameter edit distance
        # heuristic = lambda x:

        while opened:
            curr = heapq.heappop(opened)
            goal_mismatch = compound_task.check_effects(curr[1].post_bound_state)
            if not any(goal_mismatch):
                goal_reached = True
                break
            for task_name, abs_task in self.tasks.items():
                if task_name == 'utterance_abs':
                    continue
                precon_potentials = []
                precon_match_list = []
                precon_variables = {}
                for precon_idx, precon in enumerate(abs_task.preconditions[0]):
                    precon_match_list.append(precon[0])
                    for var_idx in range(1, len(precon)):
                        if precon[var_idx] not in precon_variables:
                            precon_variables[precon[var_idx]] = []
                        precon_variables[precon[var_idx]].append((precon_idx, var_idx))
                    precon_potentials.append([])
                # TODO: change to check both positive and negative precons (not urgent)
                for s in curr[1].post_bound_state:
                    ## TODO This is really inefficient
                    # Get all bindable pairs that meet preconditions
                    if s[0] in precon_match_list:
                        # if task_name == 'pickupobject_abs':
                        #     if ('atlocation', 'agent1', 'loc 19') in curr[1].post_bound_state:
                        #         # if ('objectatlocation', 'cellphone 3', 'loc 19') in curr[1].post_bound_state:
                        #         print('step2')

                        precon_idx = precon_match_list.index(s[0])
                        precon_potentials[precon_idx].append(s)

                perms = itertools.product(*precon_potentials)
                for perm in perms:

                    test_binding = {}
                    for var, binds in precon_variables.items():
                        if len(binds) > 1:
                            if len(set([perm[bind[0]][bind[1]] for bind in binds])) > 1:
                                # variable mismatch
                                variable_mismatch_flag = True
                                break
                        test_binding[var.strip('{}')] = perm[binds[0][0]][binds[0][1]]

                    if variable_mismatch_flag:
                        variable_mismatch_flag = False
                        continue
                    ### Debugging
                    # if task_name == 'gotolocation_abs' and test_step<1:
                    #     if ('receptacleatlocation','bed 1', 'loc 19') in perm:
                    #         test_step += 1
                    #         print('step1')
                    #         print('nodes', len(opened)+len(closed))
                    # if task_name == 'pickupobject_abs' and test_step<2:
                    #     if ('atlocation','agent1', 'loc 19') in perm:
                    #         # if ('objectatlocation','cellphone 3', 'loc 19') in perm:
                    #         if ('pickupable', 'cellphone 3') in perm:
                    #             test_step += 1
                    #             print('nodes', len(opened) + len(closed))
                    #             print('step2')
                    # if task_name == 'gotolocation_abs'  and test_step<3:
                    #     if ('receptacleatlocation', 'desk 1', 'loc 7') in perm:
                    #         if ('holds','agent1', 'cellphone 3') in curr[1].post_bound_state:
                    #             test_step += 1
                    #             print('nodes', len(opened) + len(closed))
                    #             print('step3')
                    # if task_name == 'putobject_abs'  and test_step<4:
                    #     if ('holds','agent1', 'cellphone 3') in perm:
                    #         if ('atlocation','agent1', 'loc 7') in perm:
                    #             test_step += 1
                    #             print('nodes', len(opened) + len(closed))
                    #             print('step4')
                    # if task_name == 'gotolocation_abs' and test_step<5:
                    #     if ('receptacleatlocation', 'dresser 1', 'loc 4') in perm:
                    #         if ('objectatlocation', 'cellphone 3', 'loc 7') in curr[1].post_bound_state:
                    #             test_step += 1
                    #             print('nodes', len(opened) + len(closed))
                    #             print('step5')
                    # if task_name == 'pickupobject_abs' and test_step<6:
                    #     if ('atlocation', 'agent1', 'loc 4') in perm:
                    #         if ('pickupable', 'alarmclock 2') in perm:
                    #             if ('objectatlocation', 'cellphone 3', 'loc 7') in curr[1].post_bound_state:
                    #                 test_step += 1
                    #                 print('nodes', len(opened) + len(closed))
                    #                 print('step6+goal')
    ###
                    # TODO: would be great if we could check validity without deepcopy
                    successor_task = deepcopy(abs_task)
                    bind_errors = successor_task.bind_variables(test_binding)
                    if bind_errors:
                        continue
                    successor_post_state, sim_effects_errors = successor_task.sim_apply_effects(curr[1].post_bound_state)
                    if any(sim_effects_errors):
                        continue
                    if successor_post_state in closed_states:
                        continue
                    curr_heur = heuristic(successor_post_state)

                    # TODO how can we do the below more efficiently?
                    for idx, o in enumerate(opened):
                        if successor_post_state == o[1].post_bound_state:
                            if o[1].dist <= (curr[1].dist+1):
                                no_add_flag = True
                            else:
                                # TODO this never hits!
                                remove_o_idx_flag = idx
                            break

                    if no_add_flag:
                        no_add_flag = False
                        continue

                    # TODO this never hits!
                    if remove_o_idx_flag > -1:
                        del opened[remove_o_idx_flag]
                        remove_o_idx_flag = -1

                    item_data = astar_node(successor_post_state, successor_task, curr[1], curr[1].dist+1)
                    heapq.heappush(opened, (curr[1].dist + 1 + curr_heur, item_data))

            closed_states.add(frozenset(curr[1].post_bound_state))
            heapq.heappush(closed, curr)

        if goal_reached == True:
            # print('nodes', len(opened) + len(closed))
            # print('goal')
            par_task = curr[1]
            while par_task.curr_task is not None:
                compound_task.subtasks.insert(0, par_task.curr_task)
                par_task = par_task.parent_node
            if compound_task.goal:
                compound_task.subtasks[-1].goal = True
        else:
            print("No solution found")
            raise NotImplementedError


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

    # Task Decomposition:

    task_decomp = '''1. Go to the Coffee Machine.
    2. Turn on the Coffee Machine.
    3. Wait for the Coffee Machine to heat up.
    4. Pick up the Cup.
    5. Go to the Fridge1.
    6. Open the Fridge1.
    7. Pick up the Coffee grounds from Fridge1.
    8. Close the Fridge1.
    9. Go to the Sink.
    10. Fill the Cup with water from the Sink.
    11. Close the Sink.
    12. Go to the Coffee Machine.
    13. Put the Coffee grounds into the Coffee Machine.
    14. Put the Cup under the Coffee Machine.
    15. Turn on the Coffee Machine.
    16. Wait for the Coffee Machine to brew the coffee.
    17. Turn off the Coffee Machine.
    18. Pick up the Cup with brewed coffee.
    19. Enjoy your freshly brewed coffee.'''.split('\n')

    task_decomp = [s.lstrip('0123456789 .') for s in task_decomp]


    planner.add_task("primitive_task_a", primitive_task_a)
    planner.add_task("primitive_task_b", primitive_task_b)

    planner.add_method("method_task_x", method_task_x)
    planner.add_method("method_task_y", method_task_y)

    initial_state = {"condition": True}
    high_level_goal = ["method_task_x", "method_task_y"]

    for task in high_level_goal:
        planner.apply_task(task, initial_state)
