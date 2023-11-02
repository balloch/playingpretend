from common.Locatable import Locatable
from common.Type import Type
class Location(Locatable):
    def __init__(self, id, type:[Type]):
        super().__init__(id, type)