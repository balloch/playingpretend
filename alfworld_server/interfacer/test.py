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

from alfworld_server.agents.BfsAgent import BfsAgent
from alfworld_runner import think

print("hey")

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

    think(args.problem, args.domain, args.grammar)