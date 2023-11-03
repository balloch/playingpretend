from pretender.common.Type import Type
from pretender.common.Predicate import Predicate
from pretender.common.AtomicAction import AtomicAction
from pretender.common.AlfworldObject import AlfworldObject
from pretender.common.Location import Location
from pretender.common.Receptacle import Receptacle


class InitialState:
    def __init__(self, types: [Type],
                 predicates: [Predicate],
                 actions: [AtomicAction],
                 objects:[AlfworldObject],
                 locations:[Location],
                 receptacles:[Receptacle],
                 visible_receptacles:[Receptacle]):
        self.types = types
        self.predicates = predicates
        self.actions = actions
        self.objects = objects
        self.locations = locations
        self.receptacles = receptacles
        self.visible_receptacles = visible_receptacles