import argparse
import llm_planner_assistant

'''make argparser'''
parser = argparse.ArgumentParser(description='Run the game')
parser.add_argument('--api_key', type=str, default=None, help='OpenAI API key')
parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0613', help='LLM Model')
parser.add_argument('--system_prompt', type=str, default='You.', help='System prompt')
parser.add_argument('--save_messages', type=bool, default=False, help='Save messages')




if __name__ == "__main__":
    args = parser.parse_args()
    model = "gpt-3.5-turbo-0613"
    base_ai = AIChat()

    llm_planner = llm_planner_assistant(base_ai, args.api_key,args.model, args.system_prompt, args.save_messages)

        # system=system_prompt, model=model, save_messages=False, api_key=api_key)
        # Ask for objects first, then ask for story
        # How to extract actions from story? 
        #   "using the list of objects, find the relevant verbs/actions"
        # Evaluation
        #   Likert scale on sequence of actions 
        #   Individual action suggestions given a scenario