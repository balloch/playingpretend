import os
class CONSTANTS:
    class PREDICATE_TYPES:

        ATLOCATION = "atlocation"
        RECEPTACLEATLOCATION = "receptacleatlocation"
        OBJECTATLOCATION = "objectatlocation"
        INRECEPTACLE = "inreceptacle"

    class OBJECT_TYPES:

        LOCATION = "location"
        RECEPTACLE = "receptacle"

    class FILES:
        DIRECTORY = "/home/suyash/eilab/playingpretend/alfworld_server/interfacer/data"
        DOMAIN_PDDL_PATH = os.path.join(DIRECTORY, "domain.pddl")
        ORIGINAL_DOMAIN_PDDL_PATH = os.path.join(DIRECTORY, "original_domain.pddl")
        GRAMMAR_PATH = os.path.join(DIRECTORY, "alfred.twl2")
        PROBLEM_PDDL_PATH = os.path.join(DIRECTORY, "problem.pddl")
        ORIGINAL_PROBLEM_PDDL_PATH = os.path.join(DIRECTORY, "original_problem.pddl")
        TRAJ_DATA_FILE = os.path.join(DIRECTORY, "traj_data.json")
        GAME_FILE = os.path.join(DIRECTORY, "game.tw-pddl")
