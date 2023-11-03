from pretender.common.Type import Type


class Parameter:
    def __init__(self, name:str, type:Type):
        self.name = name
        self.type = type