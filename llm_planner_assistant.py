''' This file contains the code for the LLM Planner Assistant. It is responsible for a variety of high level functions 
like decomposing high level tasks into subtasks, and low level functions like classifying tasks into one of many known tasks. 
It will be interfacing with the ChatGPT model using simpleaichat to do these functions. 
The purpose of this assistant is to help the HTN Planner find a logically reasonable plan from start to goal, 
using known and primitive actions as often as possible.
'''

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

class llm_planner_assistant(): #BaseModel):

    def __init__(self, chatbot=None, **kwargs):
        # super().__init__(**kwargs)
        if chatbot is None:
            api_input = input("Please enter your API key: ")
            self.chatbot=AIChat(
                console=False,
                api_key=api_input)
        else:
            self.chatbot = chatbot(kwargs)

    def get_prompt(self, template, query, context, values_dict=None):
        if template[-3:] == 'txt':
            with open(template,'r') as f:
                template_str = f.read()
        else:
            template_str = template
        prompt_string = effify(ftext=template_str,query=query, context=context) #, **values_dict)
        return prompt_string

    def classify_text(self, text,context=None, values_dict=None):
        template = 'choice_template.txt'
        prompt = self.get_prompt(template, text, context, values_dict)
        # Your code here - interact with ChatGPT to predict the category.
        
        predicted_category = self.chatbot(prompt=prompt)
        return predicted_category


def effify(ftext,**kwargs):
    """converges a fstring and its arguments into a string"""    
    return ftext.format(kwargs)


    


# Example usage
text_input = "This is a piece of text you want to classify."
bot = llm_planner_assistant()
predicted_category = bot.classify_text(text_input)
print("Predicted Category:", predicted_category)