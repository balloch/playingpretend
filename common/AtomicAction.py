from common.Precondition import Precondition
from common.Predicate import Predicate
from common.CommandTemplate import CommandTemplate
from common.AlfworldObject import AlfworldObject
from common.Locatable import Locatable


# TODO: this should be a subclass of Task
# TODO: need to keep more explicit track of params so that unique params are known

class AtomicAction:
    def __init__(self, id: str, preconditions: [Precondition], add_effects: [Predicate],
                 del_effects: [Predicate], command_template: CommandTemplate = None):
        # super().__init__(**kwargs)
        self.id = id
        self.name = None
        self.preconditions = preconditions
        self.add_effects = add_effects
        self.del_effects = del_effects
        self.command_template = command_template

    def set_command_template(self, command_template: CommandTemplate):
        self.command_template = command_template

    def set_name(self, name:str):
        self.name = name

class AtomicActionFeedback:
    # Only if any of the attributes are not None, will there be a change conveyed
    def __init__(self, agent_location:Locatable, inventory: [AlfworldObject], objectsWithinReach:[AlfworldObject], objectWithLocationUpdate:[AlfworldObject]):
        self.agent_location = agent_location
        self.inventory = inventory
        self.objectsWithinReach = objectsWithinReach
        self.objectWithLocationUpdate = objectWithLocationUpdate