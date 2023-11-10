import os
import pathlib


current_file = pathlib.Path(__file__).parent.resolve()


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
        _data_dir = current_file.parent / 'data'
        DIRECTORY = str(_data_dir)
        DOMAIN_PDDL_PATH = os.path.join(DIRECTORY, "domain.pddl")
        ORIGINAL_DOMAIN_PDDL_PATH = os.path.join(DIRECTORY, "original_domain.pddl")
        GRAMMAR_PATH = os.path.join(DIRECTORY, "alfred.twl2")
        PROBLEM_PDDL_PATH = os.path.join(DIRECTORY, "problem.pddl")
        ORIGINAL_PROBLEM_PDDL_PATH = os.path.join(DIRECTORY, "original_problem.pddl")
        TRAJ_DATA_FILE = os.path.join(DIRECTORY, "traj_data.json")
        GAME_FILE = os.path.join(DIRECTORY, "game.tw-pddl")

    class COMMAND_MAPPING:
        mapping = {
            "gotolocation": "go to {l}",
            "pickupobject": "take {o} from {r}",
            "putobject": "put {o} in/on {r}",
        }

    class ERRORS:
        NOTHING_HAPPENS = "Nothing happens."

    class ALFWORLDENV:
        class COMMAND:
            ACTION = "action"
            TARGET = "tar"
            OBJ = "obj"

