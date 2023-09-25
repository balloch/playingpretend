import os
import json
import glob
import random
import argparse
from os.path import join as pjoin

import textworld

import textworld.gym
import gym

from alfworld.info import ALFWORLD_DATA
from alfworld.agents.utils.misc import Demangler, add_task_to_grammar

from alfworld_interfacer.agents.BfsAgent import BfsAgent

# def setup_scene(env, traj_data, r_idx, args, reward_type='dense'):
#     # scene setup
#     scene_num = traj_data['scene']['scene_num']
#     object_poses = traj_data['scene']['object_poses']
#     dirty_and_empty = traj_data['scene']['dirty_and_empty']
#     object_toggles = traj_data['scene']['object_toggles']
#
#     scene_name = 'FloorPlan%d' % scene_num
#     env.reset(scene_name)
#     env.restore_scene(object_poses, object_toggles, dirty_and_empty)
#
#     # initialize to start position
#     env.step(dict(traj_data['scene']['init_action']))
#
#     # print goal instr
#     print("Task: %s" % (traj_data['turk_annotations']['anns'][r_idx]['task_desc']))
#
#     # setup task for reward
#     env.set_task(traj_data, args, reward_type=reward_type)
#
#
# def main(args):
#     print(f"Playing '{args.problem}'.")
#
#     # start THOR
#     env = ThorEnv(player_screen_height=600,
#                  player_screen_width=600)
#
#     # load traj_data
#     root = args.problem
#     json_file = os.path.join(root, 'traj_data.json')
#     with open(json_file, 'r') as f:
#         traj_data = json.load(f)
#
#     # setup scene
#     setup_scene(env, traj_data, 0, args)
#
#     # choose controller
#     if args.controller == "oracle":
#         AgentModule = OracleAgent
#         agent = AgentModule(env, traj_data, traj_root=root, load_receps=args.load_receps, debug=args.debug)
#     elif args.controller == "oracle_astar":
#         AgentModule = OracleAStarAgent
#         agent = AgentModule(env, traj_data, traj_root=root, load_receps=args.load_receps, debug=args.debug)
#     elif args.controller == "mrcnn":
#         AgentModule = MaskRCNNAgent
#         mask_rcnn = load_pretrained_model(pjoin(ALFWORLD_DATA, "detectors", "mrcnn.pth"))
#         agent = AgentModule(env, traj_data, traj_root=root,
#                             pretrained_model=mask_rcnn,
#                             load_receps=args.load_receps, debug=args.debug)
#     elif args.controller == "mrcnn_astar":
#         AgentModule = MaskRCNNAStarAgent
#         mask_rcnn = load_pretrained_model(pjoin(ALFWORLD_DATA, "detectors", "mrcnn.pth"))
#         agent = AgentModule(env, traj_data, traj_root=root,
#                             pretrained_model=mask_rcnn,
#                             load_receps=args.load_receps, debug=args.debug)
#     else:
#         raise NotImplementedError()
#
#     print(agent.feedback)
#     while True:
#         cmd = input()
#         if cmd == "ipdb":
#             from ipdb import set_trace; set_trace()
#             continue
#
#         agent.step(cmd)
#         if not args.debug:
#             print(agent.feedback)
#
#         done = env.get_goal_satisfied()
#         if done:
#             print("You won!")
#             break
#
#
# if __name__ == "__main__":
#     description = "Play the abstract text version of an ALFRED environment."
#     parser = argparse.ArgumentParser(description=description)
#     parser.add_argument("problem", nargs="?", default=None,
#                         help="Path to a folder containing PDDL and traj_data files."
#                              f"Default: pick one at random found in {ALFWORLD_DATA}")
#     parser.add_argument("--controller", default="oracle", choices=["oracle", "oracle_astar", "mrcnn", "mrcnn_astar"])
#     parser.add_argument("--debug", action="store_true")
#     parser.add_argument('--load_receps', action="store_true")
#     parser.add_argument('--reward_config', type=str, default=pjoin(alfworld.agents.__path__[0], 'config', 'rewards.json'))
#     args = parser.parse_args()
#
#     if args.problem is None:
#         problems = glob.glob(pjoin(ALFWORLD_DATA, "**", "initial_state.pddl"), recursive=True)
#         args.problem = os.path.dirname(random.choice(problems))
#
#     main(args)


class AlfredDemangler(textworld.core.Wrapper):

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)

        demangler = Demangler(game_infos=self._game.infos)
        for info in self._game.infos.values():
            info.name = demangler.demangle_alfred_name(info.id)


def think(args):
    print(f"Playing '{args.problem}'.")
    GAME_LOGIC = {
        "pddl_domain": open(args.domain).read(),
        "grammar": open(args.grammar).read(),
    }

    # load state and trajectory files
    pddl_file = os.path.join(args.problem, 'initial_state.pddl')
    json_file = os.path.join(args.problem, 'traj_data.json')
    with open(json_file, 'r') as f:
        traj_data = json.load(f)
    GAME_LOGIC['grammar'] = add_task_to_grammar(GAME_LOGIC['grammar'], traj_data)

    # dump game file
    gamedata = dict(**GAME_LOGIC, pddl_problem=open(pddl_file).read())
    gamefile = os.path.join(os.path.dirname(pddl_file), 'game.tw-pddl')
    json.dump(gamedata, open(gamefile, "w"))

    # register a new Gym environment.
    infos = textworld.EnvInfos(won=True, admissible_commands=True, game=True, expert_plan=True)
    env_id = textworld.gym.register_game(gamefile, infos,
                                         max_episode_steps=1000000,
                                         wrappers=[AlfredDemangler])

    env = gym.make(env_id)
    # Create coordinator
    coordinator = BfsAgent(env, debug_statements=True, debug_quick_play=True)

    actions = coordinator.compute_plan()
    print("Found winning state, actions: " + str(actions))



if __name__ == "__main__":
    description = "Play the abstract text version of an ALFRED environment."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("problem", nargs="?", default=None,
                        help="Path to a folder containing PDDL and traj_data files."
                             f"Default: pick one at random found in {ALFWORLD_DATA}")
    parser.add_argument("--domain",
                        default=pjoin(ALFWORLD_DATA, "logic", "alfred.pddl"),
                        help="Path to a PDDL file describing the domain."
                             " Default: `%(default)s`.")
    parser.add_argument("--grammar",
                        default=pjoin(ALFWORLD_DATA, "logic", "alfred.twl2"),
                        help="Path to a TWL2 file defining the grammar used to generated text feedbacks."
                             " Default: `%(default)s`.")
    args = parser.parse_args()

    if args.problem is None:
        problems = glob.glob(pjoin(ALFWORLD_DATA, "**", "initial_state.pddl"), recursive=True)
        args.problem = os.path.dirname(random.choice(problems))

    think(args)

