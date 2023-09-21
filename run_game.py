import argparse
import llm_planner_assistant
import creative_assistant
from simpleaichat import AIChat

'''make argparser'''
parser = argparse.ArgumentParser(description='Run the game')
parser.add_argument('--api_key', type=str, default=None, help='OpenAI API key')
parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0613', help='LLM Model')
parser.add_argument('--system_prompt', type=str, default='You are a helpful story planner', help='System prompt')
parser.add_argument('--save_messages', type=bool, default=False, help='Save messages')


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
    model = "gpt-3.5-turbo-0613"
    base_ai = AIChat()
    planner_ai = llm_planner_assistant(base_ai, 
                                       args.api_key, 
                                       args.model, 
                                       args.system_prompt, 
                                       args.save_messages)
    creative_ai = creative_assistant(base_ai, 
                                        args.api_key, 
                                        args.model, 
                                        args.system_prompt, 
                                        args.save_messages)

        # system=system_prompt, model=model, save_messages=False, api_key=api_key)
        # Ask for objects first, then ask for story
        # How to extract actions from story? 
        #   "using the list of objects, find the relevant verbs/actions"
        # Evaluation
        #   Likert scale on sequence of actions 
        #   Individual action suggestions given a scenario

    # Example usage
    bot = llm_planner_assistant()
    query_text = "Now that I have eaten dinner I will"
    context = dict(examples=examples, categories=categories)
    predicted_category = bot.classify_text(text=query_text, 
                                        examples=examples,
                                        categories=categories)
    print("Predicted Category:", predicted_category)
