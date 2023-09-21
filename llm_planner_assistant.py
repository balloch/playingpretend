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
        super().__init__(llm=llm, 
                         api_key=api_key, 
                         model=model, 
                         system_prompt=system_prompt, 
                         save_messages=save_messages)

    def classify_text(self, text, template_override=None, **context_dict):
        if template_override is None:
            template = 'choice_template.txt'
        else:
            template = template_override
        prompt = self.get_prompt(template=template, 
                                 query=text, 
                                 context_dict=context_dict)
        # Your code here - interact with ChatGPT to predict the category.
        
        predicted_category = self.llm(prompt=prompt)
        return predicted_category




# categories = """
# [Category 1]
# **Name:** Play with my friends
# **Preconditions:** After school
# **Effects:** I will be happy

# [Category 2]
# **Name:** Attack with my sword
# **Preconditions:** To slay a dragon
# **Effects:** The dragon will die

# [Category 3]
# **Name:** Find a weapon
# **Preconditions:** Once my sword is lost
# **Effects:** I will be sad
# """




## example categories

categories = """
{Play with my friends, Attack with my sword, Find a weapon}
"""



## example examples
examples = """
[Query] 'After school I will '
[Category] Play with my friends

[Query] 'To slay a dragon I need to'
[Category] Attack with my sword

[Query] 'Once my sword is lost I must'
[Category] Find a weapon
"""

# Example usage
bot = PlannerAssistant()
query_text = "Now that I have eaten dinner I will"
context = dict(examples=examples, categories=categories)
predicted_category = bot.classify_text(text=query_text, 
                                       examples=examples,
                                       categories=categories)
print("Predicted Category:", predicted_category)

