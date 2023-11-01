from common.Type import Type
from common.Locatable import Locatable
class AlfworldObject:
    def __init__(self, name, type:Type, current_location: Locatable = None):
        self.name = name
        self.type = type
        self.current_location = current_location

    def set_location(self, location:Locatable):
        self.current_location = location

