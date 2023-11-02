from common.Type import Type
from common.Locatable import Locatable
class AlfworldObject:
    def __init__(self, id, type:Type, current_location: Locatable = None):
        self.id = id
        self.type = type
        self.current_location = current_location
        self.name = None
    def set_location(self, location:Locatable):
        self.current_location = location

    def set_name(self, name):
        self.name = name
