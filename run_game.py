import argparse
import inspect
import spacy
from simpleaichat import AIChat
import os
from getpass import getpass
from bidict import bidict
import logging
import sys

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
current_dir = os.path.dirname(os.path.abspath(__file__))


parser = argparse.ArgumentParser(description='Run the game')
parser.add_argument('--api_key', type=str, default=None, help='OpenAI API key')
parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0613', help='LLM Model')
parser.add_argument('--system_prompt', type=str, default='You are a helpful story planner', help='System prompt')
parser.add_argument('--save_messages', default=False, action='store_true', help='Save messages')
parser.add_argument('--input_allowed', default=False, action='store_true', help='whether there can be console input')
parser.add_argument('--debug', default=False, action='store_true', help='whether to print debug messages')



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

if __name__ == "__main__":
    args = parser.parse_args()
    # set the logger level according to the command line args
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.debug('A debug message!')

    ## ensure api key
    if args.api_key is None:
        api_file_path = os.path.join(current_dir, 'utils/api_key.txt')
        if "OPENAI_API_KEY" in os.environ and len(os.environ["OPENAI_API_KEY"]) > 0:
            args.api_key = os.environ["OPENAI_API_KEY"]
        elif os.path.exists(api_file_path) and os.path.getsize(api_file_path) > 0:
            with open(api_file_path, 'r') as f:
                args.api_key = f.read()  
        elif args.input_allowed is True:  # TODO balloch: do better here
            args.api_key = getpass("Please enter your API key: ")
        else:
            raise ValueError("Must provide OpenAI API key")

    system_prompt = """You are a helpful assistant. You keep your answers brief. 
    When asked for steps or a list you answer with an enumerated list. 
    Only give the answer to the question, do not expound on your answers."""

    logic_system_prompt = """This is a logical, common sense, question answering task.
    Your job is to answer questions as simply and correctly as possible.
    When asked for steps or a list, please answer in an enumerated list.
    Only give the answer to the question, do not expound on your answers."""

    creative_system_prompt = """You are a children's story teller and game designer. Be creative but concise."""

    theme = 'Find Buried Pirate Treasure'

    qa_ai = LogicAssistant(model='gpt-3.5-turbo-0613',
                           save_messages=False,
                           api_key=args.api_key, 
                           model_params = {"temperature": 0.0})
    creative_ai = CreativeAssistant(
        theme=theme,
        model='gpt-3.5-turbo-0613',
        save_messages=True,
        api_key=args.api_key, 
        model_params = {"temperature": 0.1})

    ###########
    ### Initialize story
    ###########

    story = creative_ai(f"Write a short story featuring two friends, Astro and Playmate, about {theme} that a 5 year old would understand and enjoy")
    print('story, ', story)

    gen_loc = qa_ai(f"Given the story {story}, where does the story take place? If you can't tell from the story, just say 'Location Name: The story world' \n Example: 'Location Name: <example name>' ")
    gen_loc = gen_loc.replace('Location Name:','').strip()
    print('##gen_loc?, ', gen_loc)

    # story_init_loc = qa_ai(f"Given the story '{story}' \n that takes place in {gen_loc}, what specific location within {gen_loc} where the characters most likely begin the story, before they {theme}. Only answer with the Location Name. \n Example: 'Location Name: <example_location_inside_{gen_loc}>'")
    story_init_loc = creative_ai(f"Given the story which takes place in {gen_loc}, what specific location within {gen_loc} are the characters most likely begin the story, before they {theme}? Only answer with the Location Name. \n Example: 'Location Name: <example_location_inside_{gen_loc}>'")
    # story_init_loc = story_init_loc.split('\n')
    story_init_loc = story_init_loc.replace('Location Name:','').strip()
    print('##story init loc, ', story_init_loc)


    story_points = qa_ai(f"Given the story {story}, only using sentences with one clause list the five most important actions the characters made in the story to {theme}.") # Use proper nouns instead of pronouns wherever possible")
    story_points_list = tidy_llm_list_string(story_points)
    print('##story_points, ', story_points_list)

    creative_story_points = creative_ai(f"Given the story {story}, only using sentences with one clause list the five most important actions the characters made in the story to {theme}.") # Use proper nouns instead of pronouns wherever possible")
    creative_story_points_list = tidy_llm_list_string(creative_story_points)
    print('##creative_story_points_list, ', creative_story_points_list)

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
                name = primitive_str,
                primitive_fn = primitive[1],
                )
            # imaginary_fn = lambda
            imaginary = Task(
                name = primitive_str,
                primitive_fn = getattr(im_agent, primitive_str),
                )

            real_tasks.append(real)
            imaginary_tasks.append(imaginary)

    print(real_tasks)
    print(imaginary_tasks)

    for obj, loc in real_object_map.items():
        name = obj.rstrip('1234567890_').replace('_',' ')
        print(name)
        Object(name,loc)

    print(Object.object_coll)
    story_tree = Task(
        name=theme,
        expected_start_location=story_init_loc,
        expected_visit_location=[],
        objects_required= None,
        primitive_fn = None,
        subtasks=[],
        root=True,
    )

    ## TODO balloch: automate this 
    characters = ['Astro', 'Playmate']
    the_characters = grammatical_list_str(characters)
    print('the_characters: ', the_characters)


    ############
    ### Decompose story points
    ############
    curr_root = story_tree

    story_point_list_present = [qa_ai(f"Convert the following sentence to present tense: {point}") for point in enumerate(story_points_list)]
    print('##story_point_list_present, ', story_point_list_present)


    state = {'time':0, 'loc':story_init_loc,} # 'loc_type':story_init_loc[1],}
    print('##state, ', state)

    curr_loc = story_init_loc

    all_locations = bidict({story_init_loc:0})
    for loc in real_locations:
        all_locations['r_'+str(loc)]=loc
    all_objects = bidict()
    for obj in real_object_map.keys():
        all_objects['r_'+obj]=obj

    ############
    ### Main Planner Loop
    ############
    for idx, point in enumerate(story_point_list_present):
        current_task = Task(
            name= point,
            preconditions={'start_loc':curr_loc},
        )
        # Check primitives i.e. if they have to possess something to do this story point
        #############
        ##### Primitive Decomps:
        #############
        print('##point, ', point)

        ### Objects
        get_objects = qa_ai(f"List the physical objects referenced in the sentence. \n [Example] \n Sentence: 'Do research and find evidence or maps that lead to the treasures whereabouts' \n Objects: 1. evidence \n 2. map \n 2. treasure. \n [Query] \n Sentence: '{point}' \n Objects: ")
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
                obj_possess_tf = qa_ai(f"True or False: In the sentence '{point}',  {the_characters} need to possessed or acquired {obj} to use it. ")
                print('###', obj, "possessed or acquired: ", obj_possess_tf)
                obj_use = qa_ai(f"What one verb best describes how {the_characters} use or interact with {obj} in '{point}'? If it is enough that {the_characters} simply have {obj} then say 'possess'.")  
                print('###', obj, "how used: ", obj_use)
                obj_uses.append(obj_use)

                # TODO balloch: try ground objects. if no real objects remaining, announce imaginary
                # TODO balloch: hack, currently skipping all except "possess" and that all objects are "here"
                if obj_use == 'possess':
                    current_task.add_precondition(obj_use,obj)
                    # current_task.add_subtask(Task(
                    #         name= 'goto_'+obj,
                    #         effects=[{'loc':obj.loc}],
                    #         primitive_fn=ImaginaryAgent.goto_Object, ))
                    current_task.add_subtask(Task(
                            name= 'pick_'+obj,
                            effects=[{'possess':obj}],
                            primitive_fn=ImaginaryAgent.pick_Object, ))
                    all_objects[obj]=try_grounding(obj, all_objects)



        ### Locations
        move_tf = qa_ai(f"True or False: it is possible the {the_characters} can successfully '{point}' while staying at {state['loc']}.") # \n context story: \n {story} \n .")
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
            creative_ai.llm.default_session.messages.append('temp')   # TODO balloch: this is a hack make more general
            # TODO balloch: the below should be a function than any AI can use, where the parameters passed are (1) prompt, 'while' criteria function and variables, attempt limit, and 'validation function'
            while not len(new_locs_list):
                del creative_ai.llm.default_session.messages[-1]   # TODO balloch: this is a hack make more general
                print(attempt)
                new_loc = qa_ai(f"In the context of the story {story}, what are the places within {gen_loc} where the characters would most likely need to travel from {state['loc']} to {point}? Only respond with the list of location names, nothing more. ")  #[Example]'Location Name: <example_location>'") ### TODO balloch: may need creative ai
                creative_loc = creative_ai(f"Given the story, what are the places within {gen_loc} where the characters would most likely need to travel from {state['loc']} to {point}? Only respond with the list of location names, nothing more")
                print('##next_loc?, ', new_loc)
                print('##creative_loc?, ', creative_loc)
                new_loc = new_loc.replace('Location Name:','').strip()
                new_locs_list = tidy_llm_list_string(new_loc, strip_nums=True)

                attempt += 1
                if attempt > 5:
                    raise IndexError
                
            new_locs_list = tidy_llm_list_string(new_locs_list)  #[s.lstrip('0123456789 .').rstrip(' .') for s in new_locs_list]
            # TODO balloch: check here for existing location, and replace with the grounded loc from all_locations if something similar exists
            # try to ground at least one of these locations

            # Add subtasks and preconditions from locs and goto primitives
            for loc in new_locs_list:
                current_task.add_precondition('loc',loc)
                current_task.add_subtask(Task(
                        name= 'goto_'+loc,
                        effects=[{'loc':loc}],
                        primitive_fn=ImaginaryAgent.go_To, ))
                all_locations[loc] = loc  # Needs to be a unique hashable values, but not something that collides with the real locations so I use itself

            print('##new_locs_list, ', new_locs_list)

        ## Get future location
        if idx+1 < len(story_point_list_present):
            creative_future_loc = creative_ai(f"Given the story, what is the place within {gen_loc} that {the_characters} must be before they start to {story_point_list_present[idx+1]}? Only respond with the name of one location, nothing more")
            print('creative_future_loc, ', creative_future_loc)   # where is the most likely/best starting point for a task like ________

            curr_loc = tidy_llm_list_string(creative_future_loc)[0]  #[s.lstrip('0123456789 .').rstrip(' .') for s in creative_future_loc.split('\n')][0]
            if False:  # potentially alt solution for the future
                curr_loc = qa_ai(f"Choose the location category that is most likely best to start to {story_point_list_present[idx+1]}: [Categories] \n {creative_future_loc} \n Only respond with the location name, nothing more. ")  #[Example]'Location Name: <example_location>'") ### TODO balloch: may need creative ai
            curr_loc = curr_loc.replace('Location Name:','').strip()
            print('future_loc, ', curr_loc)   # where is the most likely/best starting point for a task like ________
            # TODO balloch: check for loc already existing, 
            current_task.add_precondition('end_loc',curr_loc)
            current_task.add_subtask(Task(
                    name= 'goto_'+curr_loc,
                    effects=[{'loc':curr_loc}],
                    primitive_fn=ImaginaryAgent.go_To, ))
            if curr_loc not in all_locations:
                all_locations[curr_loc]=try_grounding(
                    new_ent=curr_loc,
                    curr_grounding=all_locations)

            # del creative_ai.default_session.messages[-1]

        ## deepen:
        str_of_subtasks = grammatical_list_str(current_task.subtasks, 'name')
        print('str_of_subtasks: ', str_of_subtasks)
        deepen_subtask = qa_ai(f"True or False:  given the story ({story}), to successfully '{point}' it was enough for {the_characters} to {str_of_subtasks}.") # \n context story: \n {story} \n .")
        # TODO balloch: add the schema for this question that breaks it down into "Subject" "Verb" "Object"
        add_subtask = creative_ai(f"Given the story and the answer {deepen_subtask} whether the current subtasks are enough, what else needs to be done besides {str_of_subtasks} to successfully '{point}'? Describe the task in one sentence with only one verb. \n Example: 'The characters must find the dragon.'")
        
        ## order subtasks

        ## Need to update the objects per question
        # if idx+1 < len(story_point_list_present):
        #     future_precon = qa_ai(f"In the context of the story {story}, what objects must {the_characters} interact with before they can reasonably {story_point_list_present[idx+1]}? Only respond with the object names, nothing more. ")  #[Example]'Location Name: <example_location>'") ### TODO balloch: may need creative ai
        state['loc'] = curr_loc
        state['time'] += 1  # TODO balloch: add time to tasks
        print('##state,' , state)

        curr_root.subtasks.append(current_task)


    
    #############
    ### Visualize the story tree
    #############

    # Visualize the task tree and render the graph
    dot_graph = visualize_task_tree(story_tree) #root_task)

    # Render the graph as an image in the notebook
    dot_graph.format = 'png'
    dot_graph.render("task_tree", view=True)


    #############
    ### Run the story tree
    #############
    # TODO balloch: persistant states in execution!! pub sub model?
    state['loc'] = story_init_loc
    story_tree()



