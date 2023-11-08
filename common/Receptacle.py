import math
from common.Locatable import Locatable
from common.Type import Type
class Receptacle(Locatable):
    def __init__(self, id, type:[Type] = None, location:Locatable = None):
        super().__init__(id, type)
        self.current_location = location
        self.locs = None

    def set_location(self, location:Locatable):
        self.current_location = location

    def set_coords(self, locs):
        self.locs = locs

    def get_coords_list(self):
        if self.locs is None:
            return None
        return [self.locs['x'], self.locs['y'], self.locs['z']]

def dist_between(recep_a: Receptacle, recep_b: Receptacle):
    coords_a, coords_b = recep_a.get_coords_list(), recep_b.get_coords_list()
    sum = 0
    for coord in zip(coords_a, coords_b):
        sum += (coord[0] - coord[1])**2
    return math.sqrt(sum)