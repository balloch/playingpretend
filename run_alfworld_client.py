from logging import root
from copy import deepcopy
import time
import os
import json
import argparse
import requests
import jsonpickle
import bidict
from getpass import getpass


from alfworld_server.client_tools import get_initial_state, perform_action
from common.Task import Task
from common.Location import Location
from common.Receptacle import Receptacle
from pretender.htn import HTNPlanner
from pretender.assistants import LogicAssistant, CreativeAssistant
from pretender.utils.llm_utils import tidy_llm_list_string, grammatical_list_str
from pretender.utils.viz_utils import visualize_task_tree
from pretender.utils.planning_utils import try_grounding
from pretender.templates.gen_prompts import (logic_system_prompt,
                                             creative_system_prompt)
from pretender.templates.func_prompts import f_prompt, known_f_prompts
from pretender.test.dummy_api import ImaginaryAgent


## Path to current directory
file_dir = os.path.dirname(os.path.abspath(__file__))


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
parser.add_argument('--demo', type=str, default=None, help='static or live demo. default of None is live')
parser.add_argument('--demo_files', type=str, default='sample_data/demo_data', help='directory of static demo files')
parser.add_argument('--theme', type=str, default='Find Buried Pirate Treasure', help='theme of the story')


def change_location_tasks(current_task, point, qa_ai, creative_ai, characters, the_characters, task_decomp_stack, curr_loc):
    move_tf = qa_ai(f_prompt(prompt_in='tf_change_loc', point=point, loc=curr_loc, the_characters=the_characters))
    if move_tf[0:4] == 'True':
        move_tf = True
    elif move_tf[0:5] == 'False':
        move_tf = False
    else:
        raise TypeError

    if move_tf is False:
        new_locs_list = []
        attempt = 0
        creative_ai.llm.default_session.messages.append('temp')  # TODO balloch: this is a hack make more general
        # TODO balloch: the below should be a function than any AI can use, where the parameters passed are (1) prompt, 'while' criteria function and variables, attempt limit, and 'validation function'
        while not len(new_locs_list):
            del creative_ai.llm.default_session.messages[-1]  # TODO balloch: this is a hack make more general
            print(attempt)
            new_loc = qa_ai(
                f"In the context of the story {story}, what are the places within {gen_loc} where the characters would most likely need to travel from {state['loc']} to {point}? Only respond with the list of location names, nothing more. ")  # [Example]'Location Name: <example_location>'") ### TODO balloch: may need creative ai
            print('##next_loc?, ', new_loc)
            if False:
                creative_loc = creative_ai(
                    f"Given the story, what are the places within {gen_loc} where the characters would most likely need to travel from {state['loc']} to {point}? Only respond with the list of location names, nothing more")
                print('##creative_loc?, ', creative_loc)
            new_loc = new_loc.replace('Location Name:', '').strip()
            new_locs_list = tidy_llm_list_string(new_loc, strip_nums=True)

            attempt += 1
            if attempt > 5:
                raise IndexError

        new_locs_list = tidy_llm_list_string(
            new_locs_list)  # [s.lstrip('0123456789 .').rstrip(' .') for s in new_locs_list]
        # TODO balloch: check here for existing location, and replace with the grounded loc from all_locations if something similar exists
        # try to ground at least one of these locations

        # Add subtasks and preconditions from locs and goto primitives
        for loc in new_locs_list:
            current_task.add_precondition('loc', loc)
            current_task.add_subtask(Task(
                description='goto_' + loc,
                # TODO balloch: fix obj_use to differentiate between full response and verb
                name='goto_' + loc,
                effects=[{'loc': loc}],
                primitive_fn=ImaginaryAgent.go_To, ))
            all_locations[
                loc] = loc  # Needs to be a unique hashable values, but not something that collides with the real locations so I use itself

    ## Get future location
    if idx + 1 < len(story_point_list_present):
        creative_future_loc = creative_ai(
            f"Given the story, what is the place within {gen_loc} that {the_characters} must be before they start to {story_point_list_present[idx + 1]}? Only respond with the name of one location, nothing more")
        print('creative_future_loc, ',
              creative_future_loc)  # where is the most likely/best starting point for a task like ________

        curr_loc = tidy_llm_list_string(creative_future_loc)[
            0]  # [s.lstrip('0123456789 .').rstrip(' .') for s in creative_future_loc.split('\n')][0]
        if False:  # potentially alt solution for the future
            curr_loc = qa_ai(
                f"Choose the location category that is most likely best to start to {story_point_list_present[idx + 1]}: [Categories] \n {creative_future_loc} \n Only respond with the location name, nothing more. ")  # [Example]'Location Name: <example_location>'") ### TODO balloch: may need creative ai
        curr_loc = curr_loc.replace('Location Name:', '').strip()
        print('future_loc, ', curr_loc)  # where is the most likely/best starting point for a task like ________
        # TODO balloch: check for loc already existing,
        current_task.add_precondition('end_loc', curr_loc)
        current_task.add_subtask(Task(
            description='goto_' + curr_loc,
            name='goto_' + curr_loc,
            effects=[{'loc': curr_loc}],
            primitive_fn=ImaginaryAgent.go_To, ))
        if curr_loc not in all_locations:
            all_locations[curr_loc] = try_grounding(
                new_ent=curr_loc,
                curr_grounding=all_locations)

    return new_locs_list


def get_object_tasks(task, point, qa_ai, characters, the_characters, task_decomp_stack):
    get_objects = qa_ai(f_prompt(prompt_in='obj_in_sentence', point=point))
    get_objects = tidy_llm_list_string(get_objects)

    ## Ensure no characters in objects:
    for ch in characters:
        if ch in get_objects:
            get_objects.remove(ch)

    print('##get_objects, ', get_objects)
    # need_item_tf = qa_ai(f"True or False: In the story: \n {story} \n is it necessary to 'have' {get_objects} to {point_present}?")
    # need_item_tf = qa_ai(f"In the story: \n {story} \n For the characters to {point_present} what physical items are necessary besides {get_objects}?")  ## Doesn't work tooo complex
    task.objects_required = get_objects
    obj_uses = []
    if len(get_objects) > 0:
        for obj in get_objects:
            obj_possess_tf = qa_ai(
                f_prompt(prompt_in='tf_obj_possession', point=point, obj=obj, the_characters=the_characters))
            print('###', obj, "possessed or acquired: ", obj_possess_tf)
            obj_use = qa_ai(
                f"What one-word action best describes how {the_characters} use or interact with {obj} in '{point}'? If it is enough that {the_characters} simply have {obj} then say 'possess'.")
            print('###', obj, "how used: ", obj_use)
            obj_uses.append(obj_use)

            # TODO balloch: try ground objects. if no real objects remaining, announce imaginary
            # TODO balloch: hack, currently skipping all except "possess" and that all objects are "here"
            if obj_use == 'possess':
                task.add_precondition(obj_use, obj)
                # TODO balloch: design task reuse around "pick"
                task.add_subtask(Task(
                    description=obj_use,
                    # TODO balloch: fix obj_use to differentiate between full response and verb
                    name='pick_' + obj,
                    effects=[{'possess': obj}],
                    primitive_fn=ImaginaryAgent.pick_Object))
                # all_objects[obj] = try_grounding(obj, all_objects)
            else:
                pass
                new_compound_task = Task(
                    description=obj_use,
                    # TODO balloch: fix obj_use to differentiate between full response and verb
                    name='pick_' + obj,
                    effects=[{'possess': obj}],
                )
                task_decomp_stack.append(new_compound_task)
                task.add_subtask(new_compound_task)
    return get_objects


def imagine_decomp(story, qa_ai, creative_ai, task_decomp_stack, root, characters, init_loc, max_depth, imag_tasks):
    """
    Main Imaginary Planner Loop
    """
    the_characters = grammatical_list_str(characters)

    while len(task_decomp_stack):

        current_task = task_decomp_stack[-1]
        if current_task.visited_planner:
            # imaginary_tasks.append(current_task)
            task_decomp_stack.pop()
            continue

        # Check primitives i.e. if they have to possess something to do this story point

        # Get Objects
        curr_task_objects = get_object_tasks(current_task,
                                             current_task.name,
                                             qa_ai, characters,
                                             the_characters,
                                             task_decomp_stack)

        # New Locations
        new_task_locations, next_location = change_location_tasks(current_task,
                                                                  current_task.name,
                                                                  qa_ai,
                                                                  characters,
                                                                  the_characters,
                                                                  task_decomp_stack)

        # Deepen:
        str_of_subtasks = grammatical_list_str(current_task.subtasks, 'name')
        print('str_of_subtasks: ', str_of_subtasks)
        nondeepen_response = qa_ai(f_prompt(prompt_in='tf_deepening', point=current_task.name))
        if nondeepen_response[0:4] == 'True':
            deepen_tf = False
        elif nondeepen_response[0:5] == 'False':
            deepen_tf = True
        else:
            raise TypeError
        if deepen_tf:
            # TODO balloch: add the schema for this question that breaks it down into "Subject" "Verb" "Object"
            # TODO : this should probably be a loop
            deepen_description = creative_ai(
                prompt=f"Given the story and that it is {deepen_tf} that the current task needs another subtask, what else needs to be done besides {str_of_subtasks} to successfully '{current_task.name}'? Describe the task in one sentence with only one verb. \n Example: 'The characters must find the dragon.'"),

            print('##deepen_subtask, ', deepen_description)
            if current_task.depth < max_depth:
                deepen_subtask = Task(
                    name=deepen_description
                )
                current_task.add_subtask(deepen_subtask)
                task_decomp_stack.append(deepen_subtask)  # Append the subtask to the stack
            else:
                deepen_subtask = deepcopy()
                new_task = deepcopy(imag_tasks['utterance_abs'])

        # Order subtasks
        str_of_subtasks = grammatical_list_str(current_task.subtasks, 'name')  # Update list
        # TODO Priority 1: use an output schema here and make a general template! Reordering is a repeatable function!
        true_order = creative_ai(
            prompt=f"Given a list of subtasks of '{current_task.name},' reorder the list in the most logical order. List: \n  {str_of_subtasks} ")
        # Assuming that true_order is a list of numbers
        current_task.reorder_subtasks(true_order)

        # TODO : repair plan: assuming the current task now has a complete set of subtasks ensure precons and effects match for all

        # TODO: update curr loc properly
        # curr_loc = next_loc

        # curr_root.subtasks.append(current_task)
    return root


def imagine(args):

    theme = args.theme

    qa_ai = LogicAssistant(
        model=args.model,
        system_prompt=logic_system_prompt,
        save_messages=False,
        api_key=args.api_key,
        model_params={"temperature": 0.0})
    creative_ai = CreativeAssistant(
        theme=theme,
        model=args.model,
        system_prompt=creative_system_prompt,
        save_messages=True,
        api_key=args.api_key,
        model_params={"temperature": 0.1})

    ###########
    ### Initialize story
    ###########

    story = creative_ai(
        f"Write a short story featuring two friends, Astro and Playmate, about {theme} that a 5 year old would understand and enjoy")
    print('story, ', story)

    gen_loc = qa_ai(
        f"Given the story {story}, where does the story take place? If you can't tell from the story, just say 'Location Name: The story world' \n Example: 'Location Name: <example name>' ")
    gen_loc = gen_loc.replace('Location Name:', '').strip()
    print('##gen_loc?, ', gen_loc)

    # story_init_loc = qa_ai(f"Given the story '{story}' \n that takes place in {gen_loc}, what specific location within {gen_loc} where the characters most likely begin the story, before they {theme}. Only answer with the Location Name. \n Example: 'Location Name: <example_location_inside_{gen_loc}>'")
    story_init_loc = creative_ai(
        f"Given the story which takes place in {gen_loc}, what specific location within {gen_loc} are the characters most likely begin the story, before they {theme}? Only answer with the Location Name. \n Example: 'Location Name: <example_location_inside_{gen_loc}>'")
    # story_init_loc = story_init_loc.split('\n')
    story_init_loc = story_init_loc.replace('Location Name:', '').strip()
    print('##story init loc, ', story_init_loc)

    story_points = qa_ai(
        f"Given the story {story}, only using sentences with one clause list the five most important actions the characters made in the story to {theme}.")  # Use proper nouns instead of pronouns wherever possible")
    story_points_list = tidy_llm_list_string(story_points)
    story_point_list_present = [qa_ai(f"Convert the following sentence to present tense: {point}") for point in story_points_list]

    # TODO: automatically detect this
    characters = ['Astro', 'Playmate']
    # print('the_characters: ', the_characters)
    # print('##story_point_list_present, ', story_point_list_present)
    # print('##story_points, ', story_points_list)

    # Init tasks
    imag_root = Task(
        name=theme,
        expected_start_location=story_init_loc,
        expected_visit_location=[],
        objects_required=None,
        primitive_fn=None,
        subtasks=[],
        root=True,
    )

    imag_tasks = {'utterance_abs': Task(
        name='utterance_abs',
        primitive_fn=print,
    )
    }

    # TODO initialize truth state based on story
    # state = {'time': 0, 'loc': story_init_loc, }  # 'loc_type':story_init_loc[1],}
    # print('##state, ', state)

    curr_loc = story_init_loc

    #############
    ### Initialize the task stack
    #############
    task_decomp_stack = []

    for idx, point in enumerate(story_point_list_present):
        sp_task = Task(
            name=point,
            preconditions={'start_loc': curr_loc})
        imag_root.subtasks.append(sp_task)
        task_decomp_stack.append(sp_task)

    imag_root = imagine_decomp(
        qa_ai=qa_ai,
        creative_ai=creative_ai,
        story=story,
        task_decomp_stack=task_decomp_stack,
        root=imag_root,
        characters=characters,
        curr_loc=curr_loc,
        max_depth=args.story_depth,
        imag_tasks=imag_tasks
    )

    return story_point_list_present


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


def main(args):
    ## Fill truth table state
    init = get_initial_state()
    real_objects = {}
    real_receptacles = {}
    for _, obj in init.objects.items():
        if obj.current_location is not None:
            if obj.name is None:
                print('Warning: unnamed object:', obj)
                continue
            real_objects[obj.name] = obj
    for _, recept in init.receptacles.items():
        if recept.current_location is not None:
            real_receptacles[recept.name] = recept
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

    imag_plan = imagine(args)

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

    ## Simulate planner & variable binding
    if args.demo == 'static':
        with open(os.path.join(args.demo_files,'taskspec.json'), 'r') as f:
            task_spec = json.load(f)['task_spec']

        with open(os.path.join(args.demo_files,'imaginary.json'), 'r') as f:
            printstory = json.load(f)['printstory']

        for i, ts in enumerate(task_spec):
            new_task = deepcopy(real_tasks[ts[0]])
            new_task.bind_variables(ts[1])
            real_root.add_subtask(new_task)
        real_root.subtasks[-1].goal = True
    else:
        real_root = real_planner.plan(goal_root=real_root,
                                      initial_state=truth_state,
                                      bindings={'o': real_objects,
                                                'r': real_receptacles,
                                                'l': nav_locations})
        printstory = imag_plan

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
            print(f'Prelanning error, replanning needed before step {i} ')
            if len(plan_errors[1]):
                print(f'Errors: presence of {plan_errors[1]}')
            if len(plan_errors[0]):
                print(f'Errors: absence of {plan_errors[0]}')
        # print(f'response {i}:', history[-1].__dict__)
        print(printstory[i])
        i += 1
        if curr_task.goal == True:
            print('Goal Reached!!')
            break
        else:
            time.sleep(3)
            pass


if __name__ == "__main__":
    args = parser.parse_args()

    # ensure api key
    if args.api_key is None:
        api_file_path = os.path.join(file_dir, 'pretender/utils/api_key.txt')
        if "OPENAI_API_KEY" in os.environ and len(os.environ["OPENAI_API_KEY"]) > 0:
            args.api_key = os.environ["OPENAI_API_KEY"]
        elif os.path.exists(api_file_path) and os.path.getsize(api_file_path) > 0:
            with open(api_file_path, 'r') as f:
                args.api_key = f.read()
        elif args.input_allowed is True:  # TODO balloch: do better here
            args.api_key = getpass("Please enter your API key: ")  # This isn't hitting
        else:
            raise ValueError("Must provide OpenAI API key")
        args.api_key = args.api_key.strip()  # sometimes weird hidden chars

    main(args)