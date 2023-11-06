from logging import root

import requests
import jsonpickle
from common.Task import Task

def get_initial_state():
    r = requests.get('http://localhost:8000/v1/env')
    return jsonpickle.loads(r.json())

def perform_action(command):
    r = requests.post('http://localhost:8000/v1/action', data=command)
    return jsonpickle.loads(r.json())

def process_init(init, objects, ):
    truth_state = set()
    for objname, obj in init.objects.items():
        # objectAtLocation
        if obj.current_location is not None:
            continue
        # if isinstance(obj.current_location, common.Location.Location)
        #     for name,obj in entities.items():
        #         pass
    return truth_state

def process_response(state, response):
    pass

if __name__ == "__main__":
    ## Fill truth table state
    init = get_initial_state()
    real_tasks = init.actions
    real_objects = [obj for objname, obj in init.objects.items() if obj.current_location is not None]
    real_receptacles = init.receptacles
    nav_locations = init.visible_receptacles
    truth_state = process_init(init)
    truth_state.add( ('atlocation', 'agent1', str(init.objects['agent1'].current_location.id)) )
    print(truth_state)



    ## Preconditions come from the agreed upon goal
    root_task = Task(
        name='FindDeskLamp',
        preconditions=[
            ('objectType', '?object', 'DeskLampType'),
            ('objectAtLocation', '?object', '?location')
        ],
        root=True
    )


    ## Manual task decomposition planning


    ## Execute Plan
    goal = False  ## For testing
    i = 3 ## For testing
    while not goal:
        action, goal = root_task(state=truth_state)
        if i == 1:
            response = perform_action("go to desk 1")
        elif i == 2:
            response = perform_action("take mug 1 from desk 1")
        elif i == 3:
            response = perform_action("put mug 1 in/on desk 1")
        else:
            goal = True

        # Update State
        process_response(truth_state, response)
        i+=1

# (:goal
#  ( and
#  (objectType ?ot DeskLampType)
# ))
