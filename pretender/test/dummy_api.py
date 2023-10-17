import numpy as np
import time 

from pretender.htn import Object


## Dummy robot API functions
## Assumption: manually need to specify expected effect for primitives
class RobotAPI:
    def __init__(self, init_loc, real_graph=None, inventory=None):
        self.curr_loc = init_loc
        self.graph = real_graph
        if inventory is None:
            self.inventory = {}  ## items are <hash: object>
        elif isinstance(inventory,dict):
            self.inventory = inventory
        else:
            raise TypeError('only "None" and "dict" allowed right now')
        self._errors = []

    def _move(self, dir='forward'):
        if dir != 'forward':
            raise NotImplementedError('Only forward motion currently implemented')
        return NotImplementedError('still using teleportation')

    def _turn(self, dir):
        if dir not in ('right', 'left'):
            raise NotImplementedError('Only left and right turns currently implemented')
        return NotImplementedError('still using teleportation')

    def wait(self, waittime):
        time.sleep(waittime)

    def utterance(self, utter_str):
        # TODO: add some sort of popup bubble?
        print(utter_str)

    def go_To(self, loc):
        ## TODO: currently teleport. Add A* and use _move and _turn
        if len(self._errors) > 0:
            self._errors = []
        self.curr_loc = loc
        print('Winning!')
        return self._errors

    def go_To_Object(self, obj, loc=None):
        obj_loc = obj.loc
        return self.go_To(obj_loc)

    def pick_Object(self, obj, id=None):
        if len(self._errors) > 0:
            self._errors = []
        if isinstance(obj, str) and (obj, self.curr_loc) in Object.object_coll:
            real_obj = Object.object_coll[obj, self.curr_loc][0]
        elif isinstance(obj, Object) and real_obj.loc == self.curr_loc:
            real_obj = obj
        else:
            self._errors.append(f'No object {real_obj} at {self.curr_loc}')
            return self._errors
        self.inventory[hash] = real_obj
        real_obj.move('inventory')
        return self._errors

    def put_Object(self, obj, id=None):
        if len(self._errors) > 0:
            self._errors = []
        ## Find object in inventory:
        if isinstance(obj, str):
            for hash, inv_obj in self.inventory.items():
                if inv_obj.name == obj:
                    real_obj = inv_obj
                    break
        elif isinstance(obj, Object):
            hash = obj.__hash__()
            if hash in self.inventory:
                real_obj = obj
        else:
            self._errors.append(f'No object {real_obj} in inventory')
            return self._errors
        del self.inventory[hash]
        real_obj.move(self.curr_loc)
        return self._errors

    def use_Object(self, obj, func=None, id=None, obj2=None, id2=None):
        if len(self._errors) > 0:
            self._errors = []
        if isinstance(obj, str):
            for hash, inv_obj in self.inventory.items():
                if inv_obj.name == obj:
                    real_obj = inv_obj
                    break
        elif isinstance(obj, Object):
            hash = obj.__hash__()
            if hash in self.inventory:
                real_obj = obj
        else:
            self._errors.append(f'No object {real_obj} in inventory')
            return self._errors
        if real_obj.use_fn is not None:
            real_obj.use_fn(func=func)
        else:
            self._errors.append(f'Object {real_obj} has no such use')
            return self._errors
        return self._errors



## Imaginary matching primitive_fns
## TODO balloch there should be some clever way to make this automatic with LLMs, shouldn't have to specify
class ImaginaryAgent:
    def __init__(self, init_loc, imaginary_graph=None, inventory=None):
        self.curr_loc = init_loc
        self.graph = imaginary_graph
        if inventory is None:
            self.inventory = {}  ## items are <hash: object>
        elif isinstance(inventory,dict):
            self.inventory = inventory
        else:
            raise TypeError('only "None" and "dict" allowed right now')
        self._errors = []

    def go_To(self, loc):
        ## TODO balloch: currently teleport. Add A* and use _move and _turn
        if len(self._errors) > 0:
            self._errors = []
        self.curr_loc = loc
        print('Winning!')
        return self._errors

    def go_To_Object(self, obj, loc=None):
        obj_loc = obj.loc
        return self.go_To(obj_loc)

    def pick_Object(self, obj, id=None):
        if len(self._errors) > 0:
            self._errors = []
        if isinstance(obj, str) and (obj, self.curr_loc) in Object.object_coll:
            real_obj = Object.object_coll[obj, self.curr_loc][0]
        elif isinstance(obj, Object) and real_obj.loc == self.curr_loc:
            real_obj = obj
        else:
            self._errors.append(f'No object {real_obj} at {self.curr_loc}')
            return self._errors
        self.inventory[hash] = real_obj
        real_obj.move('inventory')
        return self._errors

    def put_Object(self, obj, id=None):
        if len(self._errors) > 0:
            self._errors = []
        ## Find object in inventory:
        if isinstance(obj, str):
            for hash, inv_obj in self.inventory.items():
                if inv_obj.name == obj:
                    real_obj = inv_obj
                    break
        elif isinstance(obj, Object):
            hash = obj.__hash__()
            if hash in self.inventory:
                real_obj = obj
        else:
            self._errors.append(f'No object {real_obj} in inventory')
            return self._errors
        del self.inventory[hash]
        real_obj.move(self.curr_loc)
        return self._errors

    def use_Object(self, obj, func=None, id=None, obj2=None, id2=None):
        if len(self._errors) > 0:
            self._errors = []
        if isinstance(obj, str):
            for hash, inv_obj in self.inventory.items():
                if inv_obj.name == obj:
                    real_obj = inv_obj
                    break
        elif isinstance(obj, Object):
            hash = obj.__hash__()
            if hash in self.inventory:
                real_obj = obj
        else:
            self._errors.append(f'No object {real_obj} in inventory')
            return self._errors
        if real_obj.use_fn is not None:
            real_obj.use_fn(func=func)
        else:
            self._errors.append(f'Object {real_obj} has no such use')
            return self._errors
        return self._errors
    

real_object_map = {
    'refrigerator_1':2,
    'refrigerator_2':3,
    'kitchen_island_1':5,
    'electric_kettle_1':4,
    'electric_kettle_2':4,
    'coffee_machine_1':5,
    'coffee_machine_2':6,
    'microwave_1':7,
    'microwave_2':7,
    'coffee_can_1':4,
    'tea_can_1':4,
    'door_1':1,
    'garbage_can_1':5,
    'garbage_can_door_1':5,
    'sink_1':5,
    'fork_1':4,
    'spoon_1':4,
    'knife_1':4,
}


objects_stripped = [s.rstrip('01234567890_').replace('_',' ') for s in real_object_map.keys()]
real_object_types = set(objects_stripped)
real_locations = set(real_object_map.values())


themes = [
    'Being a Waiter/Waitress',
    'Being a Zookeeper',
    'Being a Florist',
    'Being a Actor/Actress',
    'Being a Chef',
    'Being a Doctor',
    'Being a Teacher',
    'Being a Detective',
    'Running a Farm',
    'Running a zoo',
    'being in the circus',
    'being an astronaut and going to outer space',
    'Saving the day as a superhero',
    'Fairies in a fairie tale',
    'Make something as a construction worker'

]