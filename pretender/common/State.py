from textworld.logic.pddl_logic import State as PddlState
import json


class State:
    def __init__(self, steps_taken: [], pddl_state: PddlState, admissable_commands: [], expert_plan):
        self.steps_taken = steps_taken
        self.pddl_state = pddl_state
        self.admissable_commands = admissable_commands
        self.expert_plan = expert_plan

    def __eq__(self, other):
        return self.pddl_state.__eq__(other.pddl_state)

    def __hash__(self):
        return hash(frozenset(self.pddl_state.facts))

    def toJSON(self):
        return {
            "admissable_commands": self.admissable_commands,
            "steps_taken": self.steps_taken,
        }

def compute_state(steps_taken, infos):
    return State(steps_taken, infos['game'].state, infos['admissible_commands'], infos['expert_plan'])