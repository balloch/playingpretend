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


class llm_planner_assistant(BaseModel):

    def __init__(self, chatbot, **kwargs):
        super().__init__(**kwargs)
        self.chatbot = chatbot(**kwargs)

    def get_prompt(self, template, query, context, values_dict=None):
        if template[-3:] == 'txt':
            with open(template,'r') as f:
                template_str = f.read()
        else:
            template_str = template
        prompt_string = effify(ftext=template_str,query=query, context=context, **values_dict)
        return prompt_string

    def classify_text(text,context=None, values_dict=None):
        template = 'choice_template.txt'
        prompt = self.get_prompt(template, text, context, values_dict)
        # Your code here - interact with ChatGPT to predict the category.
        
        predicted_category = self.chatbot(prompt)
        return predicted_category


def effify(ftext,**kwargs):
    '''converges a fstring and its arguments into a string'''    
    return ftext.format(**kwargs)


    


# Example usage
text_input = "This is a piece of text you want to classify."
predicted_category = classify_text(text_input)
print("Predicted Category:", predicted_category)