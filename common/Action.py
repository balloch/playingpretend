import typing
from Precondition import Precondition
from Predicate import Predicate
from CommandTemplate import CommandTemplate
class Action:
    def __init__(self, name: str, preconditions: [Precondition], add_effects: [Predicate],
                 del_effects: [Predicate], command_template: CommandTemplate):
        # super().__init__(**kwargs)
        self.name = name
        self.preconditions = preconditions
        self.add_effects = add_effects
        self.del_effects = del_effects
        self.command_template = command_template