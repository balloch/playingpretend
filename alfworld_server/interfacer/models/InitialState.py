from common.Type import Type
from common.Predicate import Predicate
from common.Action import Action
class InitialState:
    def __init__(self, types: [Type], predicates: [Predicate], actions: [Action]):
        self.types = types
        self.predicates = predicates
        self.actions = actions