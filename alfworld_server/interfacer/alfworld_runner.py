import os
import json
import glob
import random
from os.path import join as pjoin

import textworld

import textworld.gym
import gym

from alfworld.info import ALFWORLD_DATA
from alfworld.agents.utils.misc import Demangler, add_task_to_grammar



class AlfredDemangler(textworld.core.Wrapper):

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)

        demangler = Demangler(game_infos=self._game.infos)
        for info in self._game.infos.values():
            info.name = demangler.demangle_alfred_name(info.id)


def init_game(problem):
    domain = pjoin(ALFWORLD_DATA, "logic", "alfred.pddl")
    grammar = pjoin(ALFWORLD_DATA, "logic", "alfred.twl2")
    if problem is None:
        problems = glob.glob(pjoin(ALFWORLD_DATA, "**", "initial_state.pddl"), recursive=True)
        problem = os.path.dirname(random.choice(problems))

    print(f"Playing '{problem}'.")
    GAME_LOGIC = {
        "pddl_domain": open(domain).read(),
        "grammar": open(grammar).read(),
    }

    # load state and trajectory files
    pddl_file = os.path.join(problem, 'initial_state.pddl')
    json_file = os.path.join(problem, 'traj_data.json')
    with open(json_file, 'r') as f:
        traj_data = json.load(f)
    GAME_LOGIC['grammar'] = add_task_to_grammar(GAME_LOGIC['grammar'], traj_data)

    # dump game file
    gamedata = dict(**GAME_LOGIC, pddl_problem=open(pddl_file).read())
    gamefile = os.path.join(os.path.dirname(pddl_file), 'game.tw-pddl')
    json.dump(gamedata, open(gamefile, "w"))
    return gamefile

def create_alfworld_env(problem=None):
    gamefile = init_game(problem)
    # register a new Gym environment.
    infos = textworld.EnvInfos(won=True, admissible_commands=True, game=True, expert_plan=True, verbs=True, entities=True)
    env_id = textworld.gym.register_game(gamefile, infos,
                                         max_episode_steps=1000000,
                                         wrappers=[AlfredDemangler])

    env = gym.make(env_id)
    return env

