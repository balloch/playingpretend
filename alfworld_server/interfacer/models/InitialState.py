from common.Type import Type
from common.Predicate import Predicate
from common.AtomicAction import AtomicAction
from common.AlfworldObject import AlfworldObject
from common.Location import Location
from common.Receptacle import Receptacle

class InitialState:
    def __init__(self, types: [Type],
                 predicates: [Predicate],
                 actions: [AtomicAction],
                 objects:[AlfworldObject],
                 locations:[Location],
                 receptacles:[Receptacle]):
        self.types = types
        self.predicates = predicates
        self.actions = actions
        self.objects = objects
        self.locations = locations
        self.receptacles = receptacles