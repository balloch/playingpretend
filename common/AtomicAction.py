from common.Precondition import Precondition
from common.Predicate import Predicate
from common.CommandTemplate import CommandTemplate
class AtomicAction:
    def __init__(self, name: str, preconditions: [Precondition], add_effects: [Predicate],
                 del_effects: [Predicate], command_template: CommandTemplate = None):
        # super().__init__(**kwargs)
        self.name = name
        self.preconditions = preconditions
        self.add_effects = add_effects
        self.del_effects = del_effects
        self.command_template = command_template

    def set_command_template(self, command_template: CommandTemplate):
        self.command_template = command_template