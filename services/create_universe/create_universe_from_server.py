from common.Location import Location
from common.Receptacle import Receptacle
from common.Task import Task
from common.Universe import Universe


def is_valid_location(location):
    return isinstance(location, Location) or isinstance(location, Receptacle)


def process_objects(objects):
    objects_with_locations = [obj for obj in objects if obj.current_location is not None]
    # TODO: replace such statements with logs
    [print('Warning: unnamed object:', obj) for obj in objects_with_locations if obj.name is None]
    for obj in objects_with_locations:
        if not is_valid_location(obj.current_location):
            # TODO: should a valueerror be raised? move this sanity check to the server
            # TODO: Location objects should hold a type of either Location or Receptacle instead of checks on client
            raise ValueError('current_location should only be a location or a receptacle')
    return objects_with_locations


def process_receptacles(receptacles):
    receptacles_with_locations = [rec for rec in receptacles if rec.current_location is not None]
    return receptacles_with_locations

def process_tasks(actions, perform_action):
    ## Primitive tasks, initialized with utterance
    tasks = {'utterance_abs': Task(
        name='utterance_abs',
        primitive_fn=print,
    )
    }

    #TODO: not sure why this _abs is important. keep it for now and find way to remove it.
    for action in actions:
        tasks[action.id + '_abs'] = Task(name=action.id + '_abs')
        tasks[action.id + '_abs'].from_atomic(atomic=action,
                                                   function=perform_action)

    return tasks


def create_universe(init_state, perform_action):
    objects = process_objects(init_state.objects)
    receptacles = process_receptacles(init_state.receptacles)
    tasks = process_tasks(init_state.actions, perform_action)

    return Universe(objects, receptacles, tasks)


