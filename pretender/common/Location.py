from pretender.common.Locatable import Locatable
from pretender.common.Type import Type


class Location(Locatable):
    def __init__(self, id, type:[Type]=None):
        super().__init__(id, type)