from common.Parameter import Parameter

# TODO this should inherit from Predicate
class Effect:
    def __init__(self, name, parameters: [Parameter]):
        self.name = name
        self.parameters = parameters