from interfacer.utils.constants import CONSTANTS

import textworld
import argparse

import textworld.gym
import gym
import os
import json
from os.path import join as pjoin

from alfworld.agents.utils.misc import Demangler, add_task_to_grammar
from alfworld.info import ALFWORLD_DATA
from alfworld.env.thor_env import ThorEnv
from alfworld.agents.detector.mrcnn import load_pretrained_model
from alfworld.agents.controller import OracleAgent, OracleAStarAgent, MaskRCNNAgent, MaskRCNNAStarAgent
from common.CustomArgs import CustomArgs

def setup_scene(env, traj_data, r_idx, args, reward_type='dense'):
    # scene setup
    scene_num = traj_data['scene']['scene_num']
    object_poses = traj_data['scene']['object_poses']
    dirty_and_empty = traj_data['scene']['dirty_and_empty']
    object_toggles = traj_data['scene']['object_toggles']

    scene_name = 'FloorPlan%d' % scene_num
    env.reset(scene_name)
    env.restore_scene(object_poses, object_toggles, dirty_and_empty)

    # initialize to start position
    env.step(dict(traj_data['scene']['init_action']))

    # print goal instr
    print("Task: %s" % (traj_data['turk_annotations']['anns'][r_idx]['task_desc']))

    # setup task for reward
    env.set_task(traj_data, args, reward_type=reward_type)


def create_alfworld_env(problem=CONSTANTS.FILES.DIRECTORY):
    args = CustomArgs(problem=problem, controller="oracle", debug="store_true", load_receps="store_true",
                      reward_config= pjoin(problem, 'rewards.json'))

    print(f"Playing '{args.problem}'.")

    # start THOR
    env = ThorEnv(player_screen_height=800, player_screen_width=800)

    # load traj_data
    root = args.problem
    json_file = os.path.join(root, 'traj_data.json')
    with open(json_file, 'r') as f:
        traj_data = json.load(f)

    # setup scene
    setup_scene(env, traj_data, 0, args)


    AgentModule = OracleAgent
    agent = AgentModule(env, traj_data, traj_root=root, load_receps=args.load_receps, debug=args.debug)
    return env, agent

class AlfredDemangler(textworld.core.Wrapper):

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)

        demangler = Demangler(game_infos=self._game.infos)
        for info in self._game.infos.values():
            info.id = demangler.demangle_alfred_name(info.id)


def init_game(domain, grammar, problem, traj_data_file, gamefile):
    # domain = pjoin(ALFWORLD_DATA, "logic", "alfred.pddl")
    # grammar = pjoin(ALFWORLD_DATA, "logic", "alfred.twl2")
    # if problem is None:
    #     problems = glob.glob(pjoin(ALFWORLD_DATA, "**", "initial_state.pddl"), recursive=True)
    #     problem = os.path.dirname(random.choice(problems))

    print(f"Playing '{problem}'.")
    GAME_LOGIC = {
        "pddl_domain": open(domain).read(),
        "grammar": open(grammar).read(),
    }

    # load state and trajectory files
    pddl_file = problem
    with open(traj_data_file, 'r') as f:
        traj_data = json.load(f)
    GAME_LOGIC['grammar'] = add_task_to_grammar(GAME_LOGIC['grammar'], traj_data)

    # dump game file
    gamedata = dict(**GAME_LOGIC, pddl_problem=open(pddl_file).read())
    json.dump(gamedata, open(gamefile, "w"))
    return gamefile

def create_textworld_env(constants = CONSTANTS.FILES):
    gamefile = init_game(constants.ORIGINAL_DOMAIN_PDDL_PATH,
                         constants.GRAMMAR_PATH,
                         constants.ORIGINAL_PROBLEM_PDDL_PATH,
                         constants.TRAJ_DATA_FILE,
                         constants.GAME_FILE)
    # register a new Gym environment.
    infos = textworld.EnvInfos(won=True, admissible_commands=True, game=True, expert_plan=True, verbs=True, entities=True)
    env_id = textworld.gym.register_game(gamefile, infos,
                                         max_episode_steps=1000000,
                                         wrappers=[AlfredDemangler])

    env = gym.make(env_id)
    return env

