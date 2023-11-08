from logging import root

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
    truth_state = set()
    ## locate receptacles
    # unbound_recepts = init.visible_receptacles.copy()
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
        recept_loc_ref[recept.name] = loc.name
        truth_state.add(('receptacleAtLocation', recept, loc))

    for objname, obj in init.objects.items():
        # objectAtLocation
        if obj.current_location is None:
            continue
        if isinstance(obj.current_location, Location):
            truth_state.add(('objectAtLocation', obj, obj.current_location))
        elif isinstance(obj.current_location, Receptacle):
            truth_state.add(('objectAtLocation', obj, recept_loc_ref[obj.current_location.name]))
        else:
            raise ValueError('current_location should only be a location or a receptacle')
    return truth_state, recept_loc_ref


def process_response(state, response):
    pass


if __name__ == "__main__":
    ## Fill truth table state
    init = get_initial_state()
    real_tasks = init.actions
    real_objects = [obj for objname, obj in init.objects.items() if obj.current_location is not None]
    real_receptacles = init.receptacles
    # nav_locations = init.visible_receptacles
    truth_state, nav_locations = process_init(init)
    # truth_state.add( ('atlocation', 'agent1', str(init.objects['agent1'].current_location.id)) )
    print(len(truth_state))
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


    def checkprecons(state, predicate_list=None):
        agentloc = tuple(['objectAtLocation', init.objects['agent1'], init.objects['agent1'].current_location])
        objectloc = tuple(['receptacleAtLocation',
                           init.receptacles['desk_bar__plus_02_dot_29_bar__plus_00_dot_01_bar__minus_01_dot_15'],
                           init.receptacles['desk_bar__plus_02_dot_29_bar__plus_00_dot_01_bar__minus_01_dot_15'].current_location])
        precons = [agentloc, objectloc]
        return all(precon in state for precon in precons)


    def apply_effects(state, out_state, predicate_list=None):
        agentloc = tuple(['objectAtLocation', init.objects['agent1'], init.objects['agent1'].current_location])
        new_agentloc = tuple(['objectAtLocation',
                              init.objects['agent1'],
                              init.receptacles['desk_bar__plus_02_dot_29_bar__plus_00_dot_01_bar__minus_01_dot_15'].current_location])
        state.add(new_agentloc)
        state.remove(agentloc)

    def checkeffects(state, out_state, predicate_list=None):
        added_effects = [tuple(['objectAtLocation', init.objects['agent1'], init.objects['agent1'].current_location]) ]
        removed_effects = [tuple(['objectAtLocation',
                              init.objects['agent1'],
                              init.receptacles[
                                  'desk_bar__plus_02_dot_29_bar__plus_00_dot_01_bar__minus_01_dot_15'].current_location])
                        ]
        return all(ad in state for ad in added_effects) and all(rm in state for rm in removed_effects)


    ## Execute Plan
    history = []
    goal = False  ## For testing
    i = 1 ## For testing
    while not goal:
        # action, goal = root_task(state=truth_state)
        if i == 1:
            if checkprecons(truth_state):
                history.append(perform_action("go to desk 1"))
                agentloc = tuple(['objectAtLocation', init.objects['agent1'], init.objects['agent1'].current_location])
                new_agentloc = tuple(['objectAtLocation',
                                      init.objects['agent1'],
                                      init.receptacles[
                                          'desk_bar__plus_02_dot_29_bar__plus_00_dot_01_bar__minus_01_dot_15'].current_location])

                apply_effects(state=truth_state, out_state=history[-1], predicate_list={})
                expected = checkeffects(state=truth_state, out_state=history[-1], predicate_list={})
                print('expected: ', expected)
            ## Params:
            ## a - agent (exist)
            ## lstart - starting location (exists)
            ## r - receptacle
            ## lend - ending location
            ## Precons:
            ## (atlocation, agent, lstart)
            ## (atlocation, receptacle, lend)
            ## Effects:
            ## add((atlocation, agent, lend))
            ## remove((atloaction, agent, lstart))


        elif i == 2:
            history.append(perform_action("take mug 1 from desk 1"))
        elif i == 3:
            history.append(perform_action("put mug 1 in/on desk 1"))
        else:
            goal = True
        print(f'response {i}:', history[-1].__dict__)

        # Update State
        process_response(truth_state, history[-1])
        i += 1

# (:goal
#  ( and
#  (objectType ?ot DeskLampType)
# ))
