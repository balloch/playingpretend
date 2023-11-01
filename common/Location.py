from common.Locatable import Locatable
from common.Type import Type
class Location(Locatable):
    def __init__(self, name, type:[Type]):
        super().__init__(name, type)