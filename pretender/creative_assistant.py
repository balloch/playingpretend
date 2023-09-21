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
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field
import spacy
import json

from base_assistant import BaseAssistant


# Load the English NLP model from spaCy
nlp = spacy.load("en_core_web_sm")



class CreativeAssistant(BaseAssistant):
    def __init__(self, theme, llm=None, api_key=None, model=None, system_prompt=None, save_messages=False):
        """
        Initializes the creative assistant.
        :param theme: The theme of the creative assistant.
        """
        if system_prompt is None:
            system_prompt = """You are a world-renowned game master (GM) of tabletop role-playing games (RPGs).
                            Your job will be to come up with a fun, kid-friendly imaginary adventure.

                            Rules you MUST follow:
                            - You must be creative and unique.
                            - All names you create must be kid-friendly and easy to pronounce.
                            - You must stay on theme.
                            - remembering the creative facts it invents like locations, objects,
                              actions, tasks, characters, quest, and story, and using these facts instead
                              of creating new ones whenever possible.
                            """
        super().__init__(llm=llm, 
                         api_key=api_key, 
                         model=model, 
                         system_prompt=system_prompt, 
                         save_messages=save_messages)
        self.theme = theme

    def create_world(self):
        """
        Creates the world.
        :return: The world description.
        """


## Schema Classes
class schema_player_character(BaseModel):
    name: str = Field(description="Character name")
    race: str = Field(description="Character race")
    job: str = Field(description="Character class/job")
    story: str = Field(description="Three-sentence character history")
    feats: List[str] = Field(description="Character feats")
    equipment: List[str] = Field(description="Character equipment")


class schema_tasks(BaseModel):
    name: str = Field(description="Action name")
    preconditions: str = Field(description="Facts that must be true to take the action")
    job: str = Field(description="Effects of taking the action")


class schema_write_ttrpg_setting(BaseModel):
    """Write a fun and innovative live-action role playing scenario"""

    description: str = Field(
        description="Detailed description of the setting in the voice of the game master"
    )
    quest: str = Field(description="The challenge that the players are trying to overcome.")
    primitive_tasks: List[schema_tasks] = Field(description="The list of actions that players can do in the imaginary world. Must include both the basic actions of the world and the actions necessary to complete the quest")
    success_metric: str = Field(description="A concise, one-sentence explanation of how the players will know they have succeeded at their quest.")
    init: str = Field(description="Where does the adventure begin?")  ####### This should be determined by the real world
    name: str = Field(description="Name of the setting")
    pcs: List[schema_player_character] = Field(description="Player characters of the game")


# bot = CreativeAssistant()

# ### World Creation example
# theme = 'slaying a dragon in a cave'

# ## example categories
# classify_categories = """
# {Play with my friends, Attack with my sword, Find a weapon}
# """

# ## example examples
# classify_examples = """
# [Query] 'After school I will '
# [Category] Play with my friends

# [Query] 'To slay a dragon I need to'
# [Category] Attack with my sword

# [Query] 'Once my sword is lost I must'
# [Category] Find a weapon
# """

# classify_query_text = "Now that I have eaten dinner I will"
# context = dict(examples=classify_examples, categories=classify_categories)
# predicted_category = bot.classify_text(text=classify_query_text, 
#                                        examples=classify_examples,
#                                        categories=classify_categories)
# print("Predicted Category:", predicted_category)


# Define functions to extract unique parts of speech from text
def extract_pos(text, pos_type):
    doc = nlp(text)
    pos_set = set()

    for token in doc:
        if token.pos_ == pos_type:
            pos_set.add(token.text)

    return pos_set

def extract_pos_json(json_dict, pos_type):
    all_text = " ".join([str(value) for value in json_dict.values() if isinstance(value, str)])
    return extract_pos(all_text, pos_type)



# Your JSON data
json_data = '''
{
  "description": "Welcome to the treacherous world of Draconia, a land filled with danger and adventure. In the heart of the kingdom lies a massive cave, rumored to be the lair of a powerful dragon. The dragon, known as Drakon the Terrible, has been terrorizing the countryside, burning villages and hoarding treasure. Brave adventurers from all corners of the realm have gathered to slay the dragon and bring peace back to the land. The cave is a labyrinth of tunnels and chambers, filled with deadly traps and fierce monsters. Only the strongest and most cunning heroes have a chance of surviving the treacherous journey and emerging victorious. Do you have what it takes to face the dragon and save Draconia?",
  "quest": "Slay the dragon Drakon the Terrible and bring peace back to the kingdom of Draconia.",
  "success_metric": "The players will know they have succeeded when they have defeated Drakon the Terrible and the land is no longer plagued by his terror.",
  "init": "The adventure begins in the bustling town of Faldir, where the players meet a group of fellow adventurers who have also set their sights on slaying the dragon.",
  "name": "Draconia",
  "pcs": [
    {
      "name": "Grimbold Stonehammer",
      "race": "Dwarf",
      "job": "Warrior",
      "story": "Grimbold comes from a long line of proud dwarven warriors. He seeks to prove himself and cement his family's legacy by slaying the dragon.",
      "feats": [
        "Master of the Axe: Grimbold wields a mighty battle axe with unmatched skill, dealing devastating blows to his enemies.",
        "Dwarven Resilience: Grimbold's dwarven heritage grants him incredible resilience, allowing him to withstand even the fiercest of dragon attacks."
      ],
      "equipment": [
        "Battle Axe",
        "Dwarven Plate Armor",
        "Shield",
        "Health Potion"
      ]
    },
    {
      "name": "Elara Nightshade",
      "race": "Elf",
      "job": "Ranger",
      "story": "Elara is an expert tracker and archer, trained in the ancient arts of the elven rangers. She has dedicated her life to protecting the realm from creatures like the dragon.",
      "feats": [
        "Deadly Aim: Elara's precise aim allows her to strike vital spots with her arrows, dealing extra damage.",
        "Nature's Blessing: Elara has a deep connection with nature, allowing her to communicate with animals and gain their assistance in battle."
      ],
      "equipment": [
        "Longbow",
        "Leather Armor",
        "Dagger",
        "Potion of Invisibility"
      ]
    }
  ]
}
'''

# # Combine all the text fields into a single string
# all_text = " ".join([str(value) for value in json_data.values() if isinstance(value, str)])

# Extract nouns and verbs from the combined text
nouns = extract_pos_json(json_data, "NOUN")
verbs = extract_pos_json(json_data, "VERB")

# Print the unique nouns and verbs
print("Unique Nouns:")
for noun in nouns:
    print(noun)

print("\nUnique Verbs:")
for verb in verbs:
    print(verb)
