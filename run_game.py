import argparse
import inspect
import spacy
from simpleaichat import AIChat
import os
from getpass import getpass
from bidict import bidict
import logging
import sys
import pickle

from pretender.assistants import LogicAssistant, CreativeAssistant
from pretender.htn import Task, Object
from pretender.utils.llm_utils import tidy_llm_list_string, grammatical_list_str
from pretender.utils.viz_utils import visualize_task_tree
from pretender.utils.planning_utils import try_grounding
from pretender.test.dummy_api import RobotAPI, ImaginaryAgent, real_object_map, real_locations

# Load the English NLP model from spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download

    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
# logging.info('We processed %d records', len(processed_records))

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

"""
2 ai:
 - Game Master (creative)
 - planner assistant (can be used double duty as real decomp ai)
    - Decomposition (creative)
    - Real Decomposition (real)


ai for answering "Does <this verb/precondition from the creative> correspond to anything from <this list of verb/precondition from the real>?"

tell real decomp ai that it is a robot

How to get real tree and imaginary tree to match up?
  1. Ground init suggested objects to real world objects
  2. Ask decomp ai both about imaginary

Need "Sensors" for preconditions and effects
 - need to find correspondence between Sensor (like proximity sensor) and that can "sense" a precondition/effect like "near"

For not groundable: how do you know if it is decomposable or not?

How to determine when to decompose creative? based on perceived time:
    - if LLM thinks it will take a long time (walk to cave, fight dragon), then decompose creatively
    - if LLM thinks it will take a short time (enter cave, a spell that was casted), then by rule autoassociate-with "Say" e.g. astro says "I casted a magic missile"
"""


def main_planner(args):
    system_prompt = """You are a helpful assistant. You keep your answers brief. 
    When asked for steps or a list you answer with an enumerated list. 
    Only give the answer to the question, do not expound on your answers."""

    logic_system_prompt = """This is a logical, common sense, question answering task.
    Your job is to answer questions as simply and correctly as possible.
    When asked for steps or a list, please answer in an enumerated list.
    Only give the answer to the question, do not expound on your answers."""

    creative_system_prompt = """You are a children's story teller and game designer. 
    Be creative but concise."""

    theme = 'Find Buried Pirate Treasure'

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

    speedup = True

    if not speedup:
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
        print('##story_points, ', story_points_list)

        creative_story_points = creative_ai(
            f"Given the story {story}, only using sentences with one clause list the five most important actions the characters made in the story to {theme}.")  # Use proper nouns instead of pronouns wherever possible")
        creative_story_points_list = tidy_llm_list_string(creative_story_points)
        print('##creative_story_points_list, ', creative_story_points_list)

    else:
        story = '''Once upon a time, in a small coastal town, there were two best friends named Astro and Playmate. They loved going on adventures together and exploring the world around them. One sunny day, as they were playing on the beach, they stumbled upon an old, tattered map buried in the sand.

Excitedly, Astro and Playmate unfolded the map and saw that it led to a hidden treasure buried by pirates long ago. Their eyes sparkled with excitement as they imagined all the gold coins and shiny jewels they could find. They decided to embark on a treasure hunt, just like the brave pirates of old.

Following the map's clues, Astro and Playmate ventured into the dense forest, where they encountered tall trees and chirping birds. They walked for what felt like hours until they reached a clearing with a big, old tree in the center. The map indicated that the treasure was buried beneath it.

With their little shovels in hand, Astro and Playmate started digging eagerly. The soil was soft, and they could feel their hearts racing with anticipation. As they dug deeper, they discovered a wooden chest buried beneath the tree's roots. It was covered in moss and looked ancient.

Astro and Playmate carefully opened the chest, and their eyes widened with wonder. Inside, they found not just gold coins and jewels, but also a collection of colorful seashells, a beautiful mermaid figurine, and a handwritten letter from the pirates themselves. The letter told the story of their adventures and how they wanted someone special to find their treasure.

Astro and Playmate were overjoyed. They knew they had found something truly magical. They decided to share their discovery with the whole town, spreading joy and excitement to everyone. The treasure became a symbol of friendship and the power of imagination.

From that day on, Astro and Playmate became known as the brave adventurers who found the buried pirate treasure. They were celebrated by the townspeople, who were inspired by their courage and kindness. The treasure was displayed in the town's museum, reminding everyone of the importance of dreams and the joy of discovery.

Astro and Playmate continued to go on many more adventures together, exploring the world around them and making memories that would last a lifetime. And whenever they looked at the treasure, they were reminded of the magical day they found buried pirate treasure and the power of friendship that made it all possible.'''

        gen_loc = 'The small coastal town'

        story_init_loc = 'Beach'

        story_points = '''1. Astro and Playmate stumbled upon an old, tattered map buried in the sand.
2. They unfolded the map and decided to embark on a treasure hunt.
3. Following the map's clues, they ventured into the dense forest.
4. They dug beneath the big, old tree in the clearing, where the treasure was indicated to be buried.
5. Astro and Playmate carefully opened the wooden chest they found and discovered the hidden treasure inside.'''
        story_points_list = tidy_llm_list_string(story_points)

        creative_story_points = '''1. Astro and Playmate stumbled upon an old, tattered map buried in the sand while playing on the beach.
2. They unfolded the map and discovered that it led to a hidden treasure buried by pirates long ago.
3. Astro and Playmate followed the map's clues and ventured into the dense forest, encountering tall trees and chirping birds.
4. They reached a clearing with a big, old tree in the center, where the map indicated the treasure was buried.
5. With their little shovels in hand, Astro and Playmate eagerly dug beneath the tree's roots and discovered a wooden chest filled with treasure.'''
        creative_story_points_list = tidy_llm_list_string(creative_story_points)

    ###########
    ### Initialize planning info
    ###########
    init_robot_loc = 0
    robot_api = RobotAPI(init_robot_loc)
    im_agent = ImaginaryAgent(story_init_loc)
    ## Start with a list of lists, then turn into a

    real_tasks = []
    imaginary_tasks = []

    ## Initialize API functions as primitive tasks
    for primitive in inspect.getmembers(RobotAPI, predicate=inspect.isfunction):
        primitive_str = str(primitive[0])
        if primitive_str[0] != '_':
            ## Autoground:

            real = Task(
                description=primitive_str,
                name=primitive_str,
                primitive_fn=primitive[1],
            )
            # imaginary_fn = lambda
            imaginary = Task(
                description=primitive_str,
                name=primitive_str,
                primitive_fn=getattr(im_agent, primitive_str),
            )

            real_tasks.append(real)
            imaginary_tasks.append(imaginary)

    print(real_tasks)
    print(imaginary_tasks)

    for obj, loc in real_object_map.items():
        name = obj.rstrip('1234567890_').replace('_', ' ')
        print(name)
        Object(name, loc)

    print(Object.object_coll)
    story_tree = Task(
        description=story,
        name=theme,
        expected_start_location=story_init_loc,
        expected_visit_location=[],
        objects_required=None,
        primitive_fn=None,
        subtasks=[],
        root=True,
    )

    ## TODO: automatically detect this 
    characters = ['Astro', 'Playmate']
    the_characters = grammatical_list_str(characters)
    print('the_characters: ', the_characters)

    ############
    ### Decompose story points
    ############
    curr_root = story_tree

    story_point_list_present = [qa_ai(f"Convert the following sentence to present tense: {point}") for point in
                                enumerate(story_points_list)]
    print('##story_point_list_present, ', story_point_list_present)

    state = {'time': 0, 'loc': story_init_loc, }  # 'loc_type':story_init_loc[1],}
    print('##state, ', state)

    curr_loc = story_init_loc

    all_locations = bidict({story_init_loc: 0})
    for loc in real_locations:
        all_locations['r_' + str(loc)] = loc
    all_objects = bidict()
    for obj in real_object_map.keys():
        all_objects['r_' + obj] = obj

    #############
    ### Initialize the task stack
    #############
    task_decomp_stack = []

    for idx, point in enumerate(story_point_list_present):
        sp_task = Task(
            description=point,
            preconditions={'start_loc': curr_loc})
        curr_root.subtasks.append(sp_task)
        curr_task = decom

    ############
    ### Main Planner Loop
    ############

def decompose(current_task):
    current_task = task_decomp_stack[-1]
    if current_task.visited_planner:
        imaginary_tasks.append(current_task)
        task_decomp_stack.pop()
        continue

    # Check primitives i.e. if they have to possess something to do this story point
    #############
    ##### Primitive Decomps:
    #############
    print('##point, ', point)

    ### Objects
    get_objects = qa_ai(
        f"List the physical objects referenced in the sentence. \n [Example] \n Sentence: 'Do research and find evidence or maps that lead to the treasures whereabouts' \n Objects: 1. evidence \n 2. map \n 2. treasure. \n [Query] \n Sentence: '{point}' \n Objects: ")
    get_objects = tidy_llm_list_string(get_objects)

    ## Ensure no characters:
    for ch in characters:
        if ch in get_objects:
            get_objects.remove(ch)

    print('##get_objects, ', get_objects)
    # need_item_tf = qa_ai(f"True or False: In the story: \n {story} \n is it necessary to 'have' {get_objects} to {point_present}?")
    # need_item_tf = qa_ai(f"In the story: \n {story} \n For the characters to {point_present} what physical items are necessary besides {get_objects}?")  ## Doesn't work tooo complex
    current_task.objects_required = get_objects
    obj_uses = []
    if len(get_objects) > 0:
        for obj in get_objects:
            obj_possess_tf = qa_ai(
                f"True or False: In the sentence '{point}',  {the_characters} need to possessed or acquired {obj} to use it. ")
            print('###', obj, "possessed or acquired: ", obj_possess_tf)
            obj_use = qa_ai(
                f"What one-word action best describes how {the_characters} use or interact with {obj} in '{point}'? If it is enough that {the_characters} simply have {obj} then say 'possess'.")
            print('###', obj, "how used: ", obj_use)
            obj_uses.append(obj_use)

            # TODO balloch: try ground objects. if no real objects remaining, announce imaginary
            # TODO balloch: hack, currently skipping all except "possess" and that all objects are "here"
            if obj_use == 'possess':
                current_task.add_precondition(obj_use, obj)
                # TODO balloch: design task reuse around "pick"
                current_task.add_subtask(Task(
                    description=obj_use,
                    # TODO balloch: fix obj_use to differentiate between full response and verb
                    name='pick_' + obj,
                    effects=[{'possess': obj}],
                    primitive_fn=ImaginaryAgent.pick_Object))
                all_objects[obj] = try_grounding(obj, all_objects)
            else:
                pass
                new_compound_task = Task(
                    description=obj_use,
                    # TODO balloch: fix obj_use to differentiate between full response and verb
                    name='pick_' + obj,
                    effects=[{'possess': obj}],
                )
                task_decomp_stack.append(new_compound_task)
                current_task.add_subtask(new_compound_task)
    ## Locations
    move_tf = qa_ai(
        f"True or False: it is possible the {the_characters} can successfully '{point}' while staying at {state['loc']}.")  # \n context story: \n {story} \n .")
    print('##Unecessary to Move?, ', move_tf)
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

        print('##new_locs_list, ', new_locs_list)

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

    ## deepen:
    str_of_subtasks = grammatical_list_str(current_task.subtasks, 'name')
    print('str_of_subtasks: ', str_of_subtasks)
    deepen_response = qa_ai(
        f"[Question] \n True or False: it is possible for {the_characters} to successfully '{point}' by only {str_of_subtasks}. [Context] \n story: \n {story}.")
    if deepen_response[0:4] == 'True':
        deepen_tf = True
    elif deepen_response[0:5] == 'False':
        deepen_tf = False
        # TODO balloch: add the schema for this question that breaks it down into "Subject" "Verb" "Object"
        deepen_description = creative_ai(
            prompt=f"Given the story and the answer {deepen_response} whether the current subtasks are enough, what else needs to be done besides {str_of_subtasks} to successfully '{point}'? Describe the task in one sentence with only one verb. \n Example: 'The characters must find the dragon.'"),

        print('##deepen_subtask, ', deepen_description)
        deepen_subtask = Task(
            description=deepen_description,
            name=deepen_description
        )
        current_task.add_subtask(deepen_subtask)
        task_decomp_stack.append(deepen_subtask)  # Append the subtask to the stack

    ## TODO: order subtasks

    ## Need to update the objects per question
    # if idx+1 < len(story_point_list_present):
    #     future_precon = qa_ai(f"In the context of the story {story}, what objects must {the_characters} interact with before they can reasonably {story_point_list_present[idx+1]}? Only respond with the object names, nothing more. ")  #[Example]'Location Name: <example_location>'") ### TODO balloch: may need creative ai
    state['loc'] = curr_loc
    state['time'] += 1  # TODO balloch: add time to tasks
    print('##state,', state)

        # curr_root.subtasks.append(current_task)

    # save story tree as pickle object
    if args.save:
        with open('story_tree.pkl', 'wb') as f:
            pickle.dump(story_tree, f)

    return story_tree


if __name__ == "__main__":

    args = parser.parse_args()
    # set the logger level according to the command line args
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if args.debug:
        logging.basicConfig(level=logging.INFO)
    logging.debug('A debug message!')

    ## ensure api key
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

    #############
    ### Run the story planner
    #############
    if args.load:
        with open(args.load, 'rb') as f:
            story_tree = pickle.load(f)
    else:
        story_tree = main_planner(args)

    #############
    ### Visualize the story tree
    #############

    # Visualize the task tree and render the graph
    dot_graph = visualize_task_tree(story_tree)  # root_task)

    # Render the graph as an image in the notebook
    dot_graph.format = 'png'
    dot_graph.render("task_tree", view=True)

    #############
    ### Run the story tree
    #############
    # TODO balloch: change to persistant states in execution!! pub sub model?
    init_state = {'time': 0, 'loc': story_tree.expected_start_location, }  # 'loc_type':story_init_loc[1],}
    story_tree(state=init_state)

    ## Figure out communication between ALFworld and planner first!!
    ## Planner "client" sending one action to alfworld
    ## Server executes action and sends back next state + errors
    ## Alfworld "server" sending back the new state

    ## Advice: start with just 2 actions: goto and pick for example
    ## What does the state passed to Planner look like?
    #### Is it easier to pass the preconditions and have the server-side check them

    ## DECIDE ON HARD CODE INJECTION FANTASY WORLD ERROR: 
    ## "Oh no, goblins stole the {}"
    #### Once the planner knows that an object is necessary for a task, 
    #### we can inject the fantasy world error as a world change at the ImaginaryAgent api level
