from pretender.common.Parameter import Parameter
class Predicate:
    def __init__(self, name:str, parameters:[Parameter]):
        self.name = name
        self.parameters = parameters