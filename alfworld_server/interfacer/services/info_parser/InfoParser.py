class InfoParser:
    def parse(self, infos):
        objects = []
        current_location = None
        current_inventory = None
        state_predicates = []

        return objects, current_location, current_inventory, state_predicates