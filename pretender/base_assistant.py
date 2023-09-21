''' This file contains the code for the LLM Base Assistant,
which planning assistant and creative assistant inherit from.
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

class BaseAssistant(): #BaseModel):

    def __init__(self, llm=None, api_key=None, model=None, system_prompt=None, save_messages=False):
        """
        Initializes the assistant.
        :param llm: The LLM function to call. If None, will use simpleAIchat AIChat() with ChatGPT3.5.
        :param kwargs: Arguments to pass to the LLM model.
        :param api_key: The API key to use for the LLM model. If None, will prompt the user for it.
        :param model: The model to use for the LLM model. If None, will use gpt-3.5-turbo-0613.
        :param system_prompt: The system prompt to use for the LLM model. If None, will use the default.
        """
        if llm is None or isinstance(llm,AIChat):
            if api_key is None:
                api_key = input("Please enter your API key: ")
            if model is None:
                model='gpt-3.5-turbo-0613'
            # if system_prompt is None:
            #     system_prompt=='You are a helpful story planner'
            self.llm=AIChat(
                model=model,
                console=False,
                api_key=api_key,
                system_prompt=system_prompt,
                save_messages=save_messages)
        else:
            self.llm = llm()

    def get_prompt(self, template, query, context_dict=None):
        """
        Gets the prompt string from the template, 
        and formats that template with a query and context dictionary of other values.
        all templates use 'query' as the main question being asked the LLM
        and 'examples' for the list of examples of the LLM template.
        """
        if template[-3:] == 'txt':
            with open(template,'r') as f:
                template_str = f.read()
        else:
            template_str = template
        if context_dict is None:
            context_dict = {}
        prompt_string = self.effify(ftext=template_str,
                               query=query, 
                               context_dict=context_dict) #, **values_dict)
        return prompt_string


    def effify(self, ftext, query, context_dict=None):
        """converges a fstring and its arguments into a string. 
        query separate to require it"""
        if context_dict is None:
            context_dict = {}
        context_dict['query'] = query
        if 'examples' not in context_dict:
            context_dict['examples'] = None
        return ftext.format(**context_dict)

