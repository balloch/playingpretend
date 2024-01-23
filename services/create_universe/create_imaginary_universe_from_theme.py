# TODO: all this strings should be constants and configurable
from common.ImaginaryUniverse import ImaginaryUniverse
from pretender.utils.llm_utils import tidy_llm_list_string


class ImaginaryUniverseCreator:
    def __init__(self, qa_ai, creative_ai):
        self.qa_ai = qa_ai
        self.creative_ai = creative_ai

    def generate_story(self, theme):
        # Create a story
        story = self.creative_ai(
            f"Write a short story featuring two friends, Astro and Playmate, about {theme} that a 5 year old would understand and enjoy")
        print('story, ', story)
        return story

    def generate_general_location(self, story):
        # Get general location of the story
        general_location = self.qa_ai(
            f"Given the story {story}, where does the story take place? If you can't tell from the story, just say 'Location Name: The story world' \n Example: 'Location Name: <example name>' ")
        general_location = general_location.replace('Location Name:', '').strip()
        print('##gen_loc?, ', general_location)
        return general_location

    def generate_initial_location(self, general_location, theme):
        # story_init_loc = qa_ai(f"Given the story '{story}' \n that takes place in {gen_loc}, what specific location within {gen_loc} where the characters most likely begin the story, before they {theme}. Only answer with the Location Name. \n Example: 'Location Name: <example_location_inside_{gen_loc}>'")
        # Get initial location of the story
        initial_location = self.creative_ai(
            f"Given the story which takes place in {general_location}, what specific location within {general_location} are the characters most likely begin the story, before they {theme}? Only answer with the Location Name. \n Example: 'Location Name: <example_location_inside_{general_location}>'")
        # story_init_loc = story_init_loc.split('\n')
        initial_location = initial_location.replace('Location Name:', '').strip()
        print('##story init loc, ', initial_location)
        return initial_location

    def generate_actions(self, story, theme):
        # Get actions done in the story
        story_points = self.qa_ai(
            f"Given the story {story}, only using sentences with one clause list the five most important actions the characters made in the story to {theme}.")  # Use proper nouns instead of pronouns wherever possible")
        story_points_list = tidy_llm_list_string(story_points)
        story_point_list_present = [self.qa_ai(f"Convert the following sentence to present tense: {point}") for point in
                                    story_points_list]
        return story_point_list_present

    def create_universe(self, theme):
        story = self.generate_story(theme)
        general_location = self.generate_general_location(story)
        inital_location = self.generate_initial_location(general_location, theme)
        actions = self.generate_actions(story, theme)

        # TODO: automatically detect this
        characters = ['Astro', 'Playmate']

        return ImaginaryUniverse(theme, story, general_location, inital_location, actions, characters)
