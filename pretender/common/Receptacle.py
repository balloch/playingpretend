from pretender.common.Locatable import Locatable
from pretender.common.Type import Type


class Receptacle(Locatable):
    def __init__(self, id, type:[Type] = None, location:Locatable = None):
        super().__init__(id, type)
        self.current_location = location

    def set_location(self, location:Locatable):
        self.current_location = location