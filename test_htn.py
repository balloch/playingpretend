from logging import root
from copy import deepcopy
import time
import os
import json
import argparse
import requests
import jsonpickle

from alfworld_server.client_tools import get_initial_state, perform_action
from common.Task import Task
from common.Location import Location
from common.Receptacle import Receptacle

from pretender.htn import HTNPlanner
from pretender.assistants import LogicAssistant, CreativeAssistant
# from pretender.htn import Task, Object
from pretender.utils.llm_utils import tidy_llm_list_string, grammatical_list_str
from pretender.utils.viz_utils import visualize_task_tree
from pretender.utils.planning_utils import try_grounding
from pretender.test.dummy_api import RobotAPI, ImaginaryAgent, real_object_map, real_locations


import bidict


parser = argparse.ArgumentParser(description='Run the game')
parser.add_argument('--api_key', type=str, default=None, help='OpenAI API key')
parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0613', help='LLM Model')
parser.add_argument('--system_prompt', type=str, default='You are a helpful story planner', help='System prompt')
parser.add_argument('--save_messages', default=False, action='store_true', help='Save messages')
parser.add_argument('--input_allowed', default=False, action='store_true', help='whether there can be console input')
parser.add_argument('--debug', default=False, action='store_true', help='whether to print debug messages')
parser.add_argument('--story_depth', type=int, default=0, help='The deepest level of the story tree to generate')
parser.add_argument('--save', default=False, action='store_true', help='whether to save the story tree')
parser.add_argument('--load', type=str, default=None, help='load a story tree from a file')
parser.add_argument('--demo', type=str, default='live', help='static or live demo')
parser.add_argument('--demo_files', type=str, default='sample_data/demo_data', help='directory of static demo files')


def main(args):
    ## Fill truth table state
    init = get_initial_state()
    real_objects = {}
    real_receptacles = {}
    for _, obj in init.objects.items():
        if obj.current_location is not None:
            if obj.name is None:
                print('barf')
            real_objects[obj.name] = obj
    # real_objects = [obj for objname, obj in init.objects.items() if obj.current_location is not None]
    for _, recept in init.receptacles.items():
        if recept.current_location is not None:
            real_receptacles[recept.name] = recept

    # real_receptacles = init.receptacles
    truth_state, nav_locations = process_init(init)

    ## Primitive tasks, initialized with utterance
    # real_tasks = init.actions
    real_tasks = {'utterance_abs': Task(
        name='utterance_abs',
        primitive_fn=print,
    )
    }

    for action in init.actions:
        real_tasks[action.id+'_abs'] = Task(name=action.id+'_abs')
        real_tasks[action.id+'_abs'].from_atomic(atomic=action,
                                                 function=perform_action)

    real_planner = HTNPlanner(tasks=real_tasks)


    ## Create planner root from goal
    real_root = Task(
        name='FindAlarmClockWithCellphone',
        effects=[[
            ('objectatlocation', 'cellphone 3', 'loc 7'),
            ('holds', 'agent1', 'alarmclock 2')],
            []
        ],
        root=True,
        goal=True
    )

    real_root = real_planner.plan(goal_root=real_root,
                                  initial_state=truth_state,
                                  bindings={'o':real_objects,
                                            'r':real_receptacles,
                                            'l':nav_locations})

    ## Execute Plan
    goal = False
    history = []
    i = 0
    while not goal:
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
            print(f'Planning error, replanning needed before step {i} ')
            if len(plan_errors[1]):
                print(f'Errors: presence of {plan_errors[1]}')
            if len(plan_errors[0]):
                print(f'Errors: absence of {plan_errors[0]}')
        i += 1
        if curr_task.goal == True:
            print('Goal Reached!!')
            break
        else:
            time.sleep(3)
            pass




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



if __name__ == "__main__":
    args = parser.parse_args()
    main(args)