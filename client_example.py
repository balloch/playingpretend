from logging import root
from copy import deepcopy
import time
import requests
import jsonpickle
from common.Task import Task
from common.Location import Location
from common.Receptacle import Receptacle


# import bidict


def get_initial_state():
    r = requests.get('http://localhost:8000/v1/env')
    return jsonpickle.loads(r.json())


def perform_action(command):
    r = requests.post('http://localhost:8000/v1/action', data=command)
    return jsonpickle.loads(r.json())


def process_init(init):
    truth = set()

    ## locate receptacles
    recept_loc_ref = {}

    def recurse_recept_loc(receptacle):
        if isinstance(receptacle.current_location, Location):
            return receptacle.current_location
        elif isinstance(receptacle.current_location, Receptacle):
            return recurse_recept_loc(receptacle.current_location)
        else:
            raise ValueError('current_location should only be a location or a receptacle')

    for recept in init.receptacles.values():
        loc = recurse_recept_loc(recept)
        recept_loc_ref[recept.name.strip()] = loc.name.strip()
        truth.add(('receptacleatlocation', recept.name.strip(), loc.name.strip()))

    # recept_loc_ref = bidict(recept_loc_ref)

    # TODO : for all objects except 'agent1' add 'inreceptacle' predicate where appropriate
    for objname, obj in init.objects.items():
        # objectAtLocation
        if obj.current_location is None:
            continue
        truth.add(('pickupable', obj.name.strip()))
        if isinstance(obj.current_location, Location):
            if objname == 'agent1':
                truth.add(('atlocation', 'agent1', obj.current_location.name))
                continue
            truth.add(('objectatlocation', obj.name.strip(), obj.current_location.name.strip()))
        elif isinstance(obj.current_location, Receptacle):
            try:
                truth.add(
                    ('objectatlocation', obj.name.strip(), recept_loc_ref[obj.current_location.name.strip()]))
            except KeyError:
                print(f"skipping {obj.name}; no listed receptacle {obj.current_location.name}")
        else:
            raise ValueError('current_location should only be a location or a receptacle')
    return truth, recept_loc_ref


def process_response(state, response):
    pass


if __name__ == "__main__":
    ## Fill truth table state
    init = get_initial_state()
    real_tasks = init.actions
    real_objects = [obj for objname, obj in init.objects.items() if obj.current_location is not None]
    real_receptacles = init.receptacles
    truth_state, nav_locations = process_init(init)

    ## Create planner root from goal
    real_root = Task(
        name='FindDeskLamp',
        preconditions=[
            # ('objectType', '?object', 'DeskLampType'),
            ('objectatlocation', '?object', '?location'),
        ],
        root=True,
        goal=True
    )

    real_tasks = {}

    for action in init.actions:
        real_tasks[action.id+'_abs'] = Task(name=action.id+'_abs')
        real_tasks[action.id+'_abs'].from_atomic(atomic=action,
                                                 function=perform_action)

    ## Simulate planner & variable binding
    task_spec = [['gotolocation_abs',
                  {'?a': 'agent1',
                   '?lstart': 'loc 1',
                   '?r': 'desk 1',
                   '?lend': nav_locations['desk 1']}
                  ],
                 ['pickupobject_abs',
                  {'?a': 'agent1',
                   '?l': nav_locations['desk 1'],
                   '?r': 'desk 1',
                   '?o': 'mug 1'}
                  ],
                 ['gotolocation_abs',
                  {'?a': 'agent1',
                   '?lstart': nav_locations['desk 1'],
                   '?r': 'bed 1',
                   '?lend': nav_locations['bed 1']}
                  ],
                 ['putobject_abs',
                  {'?a': 'agent1',
                   '?l': nav_locations['bed 1'],
                   '?r': 'bed 1',
                   '?o': 'mug 1'}
                  ],
                 ]

    for i, ts in enumerate(task_spec):
        new_task = deepcopy(real_tasks[ts[0]])
        new_task.bind_variables(ts[1])
        real_root.add_subtask(new_task)
    real_root.subtasks[-1].goal = True

    ## Execute Plan
    goal = False
    history = []
    i = 0
    while not goal:
        # for curr_task in root_task(state=truth_state):
        # action, goal = root_task(state=truth_state)
        curr_task = real_root.get_next_prim()
        goal = curr_task.goal
        plan_errors = curr_task.check_precons(truth_state)
        if not any(plan_errors):
            response = real_root.execute_next(truth_state) #, command="go to desk 1")
            history.append(response)
            curr_task.apply_effects(state=truth_state, state_change=history[-1], nav_locations=nav_locations)
            plan_errors = curr_task.check_effects(state=truth_state, state_change=history[-1],
                                                  nav_locations=nav_locations)
            if any(plan_errors):
                print(f'Planning error, replanning needed at step {i} ')
                if len(plan_errors[1]):
                    print(f'Errors: presence of {plan_errors[1]}')
                if len(plan_errors[0]):
                    print(f'Errors: absence of {plan_errors[0]}')
        else:
            print(f'Prelanning error, replanning needed before step {i} ')
            if len(plan_errors[1]):
                print(f'Errors: presence of {plan_errors[1]}')
            if len(plan_errors[0]):
                print(f'Errors: absence of {plan_errors[0]}')
        # print(f'response {i}:', history[-1].__dict__)
        i += 1
        if curr_task.goal == True:
            print('Goal Reached!!')
            break
        else:
            time.sleep(3)
