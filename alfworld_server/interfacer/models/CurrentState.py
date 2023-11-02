from common.Locatable import Locatable
from common.AlfworldObject import AlfworldObject
from common.Predicate import Predicate
class CurrentState:
    def __init__(self,
                 objects:[AlfworldObject],
                 current_location:Locatable,
                 current_inventory:AlfworldObject,
                 state_predicates:[Predicate]):
        self.objects = objects
        self.current_location = current_location
        self.current_inventory = current_inventory
        self.state_predicates = state_predicates
