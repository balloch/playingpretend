''' This file contains the code for the Creative Assistant. 
The purpose of this assistant is to come up with the creating the imaginary environment
in which the players can play pretend.
Given a theme, it is responsible for functions like
 * creating the world, including,
    * the locations in the world that the players can visit
    * the objects in the world that the players can interact with
    * the action that the players can take in the world
 * creating the characters 
 * coming up with a quest for the players to do
 * coming up with a story for the players to follow
It will be interfacing with the ChatGPT model using simpleaichat to do these functions, 
remembering the creative facts it invents like locations, objects, actions, characters, 
quest, and story, and using these facts instead of creating new ones whenever possible.
'''

from simpleaichat import AIChat
import orjson
from rich.console import Console    
from getpass import getpass
from base_assistant import BaseAssistant



class creative_assistant(BaseAssistant):
    def __init__(self, llm=None, api_key=None, model=None, system_prompt=None, save_messages=False):
        """
        Initializes the creative assistant.
        :param llm: The LLM function to call. If None, will use simpleAIchat AIChat() with ChatGPT3.5.
        :param kwargs: Arguments to pass to the LLM model.
        :param api_key: The API key to use for the LLM model. If None, will prompt the user for it.
        :param model: The model to use for the LLM model. If None, will use gpt-3.5-turbo-0613.
        :param system_prompt: The system prompt to use for the LLM model. If None, will use the default.
        """
        super().__init__(llm=llm, 
                         api_key=api_key, 
                         model=model, 
                         system_prompt=system_prompt, 
                         save_messages=save_messages)
