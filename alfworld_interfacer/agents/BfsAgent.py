from alfworld_interfacer.env.WalkerResetter import WalkerResetter
from textworld.logic.pddl_logic import State as PddlState
from collections import deque

import random

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


class BfsAgent:
    def __init__(self, env, debug_statements=False, debug_quick_play=False, debug_quick_play_expert_rate=0.6):
        self.env = env
        self.debug_statements = debug_statements
        self.debug_quick_play = debug_quick_play
        self.debug_quick_play_expert_rate = debug_quick_play_expert_rate

    def compute_state(self, steps_taken, infos):
        return State(steps_taken, infos['game'].state, infos['admissible_commands'], infos['expert_plan'])

    def debug_statement(self, statement:str):
        if self.debug_statements:
            print(statement)

    def compute_plan(self):
        env_resetter = WalkerResetter()
        state_queue = deque()
        visited_states = set()

        env = self.env
        _, infos = env.reset()

        state_queue.append(self.compute_state([], infos))
        win_state = None

        while len(state_queue) != 0:
            state = state_queue.popleft()
            self.debug_statement("Currently exploring state "+str(state.steps_taken))

            admissable_actions = state.admissable_commands

            if self.debug_quick_play:
                admissable_actions = state.expert_plan
                if random.random() < self.debug_quick_play_expert_rate:
                    admissable_actions.append(random.choice(state.admissable_commands))

            if not state in visited_states:

                for action in admissable_actions:
                    self.debug_statement("Added action " + str(action))
                    env = env_resetter.reset(env, state.steps_taken)
                    _, _, done, infos = env.step(action)

                    new_steps_taken = list(state.steps_taken)
                    new_steps_taken.append(action)
                    curr_state = self.compute_state(new_steps_taken, infos)

                    if done:
                        win_state = curr_state
                        state_queue.clear()
                        break

                    if curr_state not in visited_states:
                        state_queue.append(curr_state)

            visited_states.add(state)

        return win_state.steps_taken
