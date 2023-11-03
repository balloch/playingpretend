from pretender.common.Type import Type


class Locatable:
    def __init__(self, id, type:[Type]):
        self.id = id
        self.type = type
        self.name = None

    def set_name(self, name: str):
        self.name = name