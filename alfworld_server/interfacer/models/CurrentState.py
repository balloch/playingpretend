from pretender.common.Locatable import Locatable
from pretender.common.AlfworldObject import AlfworldObject
from pretender.common.Predicate import Predicate


class CurrentState:
    def __init__(self,
                 visible_objects:[AlfworldObject],
                 receptacles: [Locatable],
                 current_inventory:[AlfworldObject],
                 current_location:Locatable,
                 objects_with_updates: [AlfworldObject],
                 error_message: str):
        self.visible_objects = visible_objects
        self.receptacles = receptacles
        self.current_inventory = current_inventory
        self.current_location = current_location
        self.objects_with_updates = objects_with_updates
        self.error_message = error_message
