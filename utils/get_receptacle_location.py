from common.Location import Location
from common.Receptacle import Receptacle

# TODO: move this functionality to the server by introducing a proper location variable guaranteed to
#  give the final location
def get_location(receptacle):
    if isinstance(receptacle.current_location, Location):
        return receptacle.current_location
    elif isinstance(receptacle.current_location, Receptacle):
        return get_location(receptacle.current_location)
    else:
        raise ValueError('current_location should only be a location or a receptacle')