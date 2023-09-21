''' This file contains the code for the LLM Planner Assistant. It is responsible for a variety of high level functions 
like decomposing high level tasks into subtasks, and low level functions like classifying tasks into one of many known tasks. 
It will be interfacing with the ChatGPT model using simpleaichat to do these functions. 
The purpose of this assistant is to help the HTN Planner find a logically reasonable plan from start to goal, 
using known and primitive actions as often as possible.
'''
from base_assistant import BaseAssistant
from simpleaichat import AIChat
import orjson
from rich.console import Console
from getpass import getpass

from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


"""
4 ai:
 - Game Master (creative)
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

class PlannerAssistant(BaseAssistant): #BaseModel):

    def __init__(self, llm=None, api_key=None, model=None, system_prompt=None, save_messages=False):
        if system_prompt is None:
            system_prompt='''
                You are a Planning Assistant. 
                You are going to be tasked with decomposing high level tasks into subtasks, 
                by classifying tasks from a set of known categories of tasks,
                coming up with logical preconditions and effects
                and reasoning about whether tasks can logically follow each other.
                Your purpose is to help the HTN Planner find a logically reasonable plan 
                from Start to Goal, using known and objects, tasks, and actions as often as possible,
                but being creative when it is not possible.
                '''
        super().__init__(llm=llm, 
                         api_key=api_key, 
                         model=model, 
                         system_prompt=system_prompt, 
                         save_messages=save_messages)

    def classify_text(self, text, template_override=None, **context_dict):
        if template_override is None:
            template = 'templates/choice_template.txt'
        else:
            template = template_override
        prompt = self.get_prompt(template=template, 
                                 query=text, 
                                 context_dict=context_dict)
        # Your code here - interact with ChatGPT to predict the category.
        
        predicted_category = self.llm(prompt=prompt)
        return predicted_category

    def decompose(self, task, template_override=None, **context_dict):
        if template_override is None:
            template = 'templates/decompose_template.txt'
        else:
            template = template_override
        prompt = self.get_prompt(template=template, 
                                 query=task, 
                                 context_dict=context_dict)
        # Your code here - interact with ChatGPT to decompose the text.
        decomposed_text = self.llm(prompt=prompt)
        return decomposed_text




bot = PlannerAssistant()

### Classify example
## example categories
classify_categories = """
{Play with my friends, Attack with my sword, Find a weapon}
"""

## example examples
classify_examples = """
[Query] 'After school I will '
[Category] Play with my friends

[Query] 'To slay a dragon I need to'
[Category] Attack with my sword

[Query] 'Once my sword is lost I must'
[Category] Find a weapon
"""

classify_query_text = "Now that I have eaten dinner I will"
context = dict(examples=classify_examples, categories=classify_categories)
predicted_category = bot.classify_text(text=classify_query_text, 
                                       examples=classify_examples,
                                       categories=classify_categories)
print("Predicted Category:", predicted_category)


### Test decompose
## example primitive tasks
decompose_primitive_tasks = """
{"Go to", "Look at", "Turn On", "Turn Off", "Pick Up","Wait for"}
"""

decompose_objects = {'Cup', 'Bear',  'Sink', 'Coffee grounds', 'Fridge1', 'Coffee Machine'}

## example examples
decompose_examples = None
decompose_query_text = "Make Coffee"
context = dict(primitive_tasks=decompose_primitive_tasks, 
               objects=decompose_objects)
decomp = bot.decompose(task=decompose_query_text, 
                       primitive_tasks=decompose_primitive_tasks, 
                       objects=decompose_objects)
print("Decomposition:", decomp)

