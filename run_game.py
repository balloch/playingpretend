import argparse
import inspect
import spacy
from simpleaichat import AIChat
import os
from getpass import getpass

from pretender.assistants import LogicAssistant, CreativeAssistant
from pretender.htn import Task, Object
from pretender.utils.llm_utils import tidy_llm_list_string
from pretender.test.dummy_api import RobotAPI, ImaginaryAgent, real_object_locations


# Load the English NLP model from spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download

    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


## Path to current directory
current_dir = os.path.dirname(os.path.abspath(__file__))


'''make argparser'''
parser = argparse.ArgumentParser(description='Run the game')
parser.add_argument('--api_key', type=str, default=None, help='OpenAI API key')
parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0613', help='LLM Model')
parser.add_argument('--system_prompt', type=str, default='You are a helpful story planner', help='System prompt')
parser.add_argument('--save_messages', default=False, action='store_true', help='Save messages')
parser.add_argument('--input_allowed', default=False, action='store_true', help='whether there can be console input')



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
    init_imaginary_loc = 'treehouse'
    robot_api = RobotAPI(init_robot_loc)
    im_agent = ImaginaryAgent(init_imaginary_loc)
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

    for obj, loc in real_object_locations.items():
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

        # How Ambient works:
        # Ask for objects first, then ask for story
        # How to extract actions from story? 
        #   "using the list of objects, find the relevant verbs/actions"
        # Evaluation
        #   Likert scale on sequence of actions 
        #   Individual action suggestions given a scenario

