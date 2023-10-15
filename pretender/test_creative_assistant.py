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

import orjson

from pretender.assistants import CreativeAssistant


###########
### Test Creative Assistant
###########



# Your JSON data
json_data = {
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


theme = 'slaying a dragon in a cave'
bot = CreativeAssistant(theme=theme)
world_structure = bot.create_world()

# context = dict(examples=classify_examples, categories=classify_categories)
# predicted_category = bot.classify_text(text=classify_query_text, 
#                                        examples=classify_examples,
#                                        categories=classify_categories)

print("world_structure: ",orjson.dumps(world_structure, option=orjson.OPT_INDENT_2).decode())
print(input())


