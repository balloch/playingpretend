from interfacer.services.command_checker.BaseChecker import BaseChecker
from interfacer.utils.constants import CONSTANTS

class InventoryCheckBeforeTake(BaseChecker):
    def command_valid(self, agent, command):
        return command[CONSTANTS.ALFWORLDENV.COMMAND.ACTION] == agent.Action.PICK

    def check_condition(self, agent, command):
        return len(agent.inventory) == 0

    def name(self):
        return "InventoryCheckBeforeTake"


class InventoryCheckBeforePut(BaseChecker):
    def command_valid(self, agent, command):
        return command[CONSTANTS.ALFWORLDENV.COMMAND.ACTION] == agent.Action.PUT

    def check_condition(self, agent, command):
        return len(agent.inventory) > 0

    def name(self):
        return "InventoryCheckBeforePut"