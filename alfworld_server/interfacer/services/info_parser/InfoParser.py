from interfacer.utils.methods import get_receptacles_from_agent
from interfacer.utils.constants import CONSTANTS
from common.Receptacle import Receptacle
from common.Location import Location
from common.AlfworldObject import AlfworldObject
class InfoParser:
    def parse_visible_objects(self, agent):
        visible_objects = None
        if agent.visible_objects:
            visible_objects = agent.visible_objects
        return visible_objects
    def parse_receptacles(self, agent):
        return get_receptacles_from_agent(agent)
    def parse_inventory(self, agent):
        return agent.inventory

    def parse_current_location(self, agent):
        curr_location = None
        if agent.curr_recep:
            curr_location = agent.curr_recep
        return curr_location

    def parse_error_message(self, agent):
        error_message = None
        if agent.feedback == CONSTANTS.ERRORS.NOTHING_HAPPENS:
            error_message = CONSTANTS.ERRORS.NOTHING_HAPPENS

        return error_message
    def parse_action(self, agent, command):
        parsed_command = agent.parse_command(command)
        objects_with_updates = []
        if parsed_command[CONSTANTS.ALFWORLDENV.COMMAND.ACTION] == agent.Action.PICK:
            obj, tar = parsed_command[CONSTANTS.ALFWORLDENV.COMMAND.OBJ], parsed_command[CONSTANTS.ALFWORLDENV.COMMAND.TARGET]
            new_location = Location("agent1")
            obj = AlfworldObject(obj, current_location=new_location)
            objects_with_updates.append(obj)
        elif parsed_command[CONSTANTS.ALFWORLDENV.COMMAND.ACTION] == agent.Action.PUT:
            obj, tar = parsed_command[CONSTANTS.ALFWORLDENV.COMMAND.OBJ], parsed_command[
                CONSTANTS.ALFWORLDENV.COMMAND.TARGET]
            new_location = Receptacle(tar)
            obj = AlfworldObject(obj, current_location=new_location)
            objects_with_updates.append(obj)

        return objects_with_updates
    def parse(self, agent, command):
        visible_objects = self.parse_visible_objects(agent)
        receptacles = self.parse_receptacles(agent)
        current_inventory = self.parse_inventory(agent)
        current_location = self.parse_current_location(agent)
        error_message = self.parse_error_message(agent)
        if error_message is None:
            objects_with_updates = self.parse_action(agent, command)
        else:
            objects_with_updates = None

        return visible_objects, receptacles, current_inventory, current_location, objects_with_updates, error_message