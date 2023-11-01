from common.Type import Type
from common.Predicate import Predicate
from common.AtomicAction import AtomicAction
class InitialState:
    def __init__(self, types: [Type], predicates: [Predicate], actions: [AtomicAction]):
        self.types = types
        self.predicates = predicates
        self.actions = actions