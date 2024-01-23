from utils.get_receptacle_location import get_location
from enums.predicates import Predicates
import constants
from Location import Location
from Receptacle import Receptacle
class Universe:
    def __create_name_maps__(self):
        self.objects_map = {obj.name: obj for obj in self.objects}
        self.receptacles_map = {rec.name: rec for rec in self.receptacles}

    # TODO: remove this method once server can provide location directly
    def __create_receptacle_location_map__(self):
        self.receptacle_location_map = {}
        for receptacle in self.receptacles:
            location = get_location(receptacle)
            self.receptacle_location_map[receptacle.name] = location

    # A lot of stripping was done in this function earlier - object names, location names.
    # They have been removed for now and if there are any issues then the server should send stripped names.
    def __create_truth_table__(self):
        self.truth_table = set()

        # Receptacle Locations
        for receptacle_name, location in self.receptacle_location_map.items():
            self.truth_table.add((Predicates.RECEPTACLE_AT_LOCATION, receptacle_name, location.name))

        # TODO : for all objects except constants.PLAYER_NAME add 'inreceptacle' predicate where appropriate
        for obj in self.objects:
            self.truth_table.add((Predicates.PICKUPABLE, obj.name))
            #TODO: server should provide player properties separately and not in objects
            if obj.name == constants.PLAYER_NAME:
                self.truth_table.add((Predicates.AT_LOCATION, constants.PLAYER_NAME, obj.current_location.name))

            if isinstance(obj.current_location, Location):
                self.truth_table.add((Predicates.OBJECT_AT_LOCATION, obj.name, obj.current_location.name))
            elif isinstance(obj.current_location, Receptacle):
                try:
                    #TODO: move this sanity check to the server. also will this ever come?
                    self.truth_table.add(
                        (Predicates.OBJECT_AT_LOCATION, obj.name, self.receptacle_location_map[obj.current_location.name]))
                except KeyError:
                    print(f"skipping {obj.name}; no listed receptacle {obj.current_location.name}")
            else:
                raise ValueError('current_location should only be a location or a receptacle')
    def __init__(self, objects, receptacles, tasks):
        self.objects = objects
        self.receptacles = receptacles
        self.tasks = tasks

        self.__create_name_maps__()
        self.__create_receptacle_location_map__()
        self.__create_truth_table__()
