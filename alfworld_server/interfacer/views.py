from django.http import HttpResponse, JsonResponse
from interfacer.alfworld_runner import create_textworld_env, create_alfworld_env
from interfacer.alfworld_env import AlfworldEnv, TextworldEnv
from common.State import compute_state
from interfacer.models.InitialState import InitialState
from interfacer.models.CurrentState import CurrentState
from interfacer.services.pddl_parser.PDDL import PDDL_Parser
from interfacer.services.info_parser.InfoParser import InfoParser
from interfacer.utils.constants import CONSTANTS
from django.views.decorators.csrf import csrf_exempt
from interfacer.services.command_checker.checkers import check as request_check
import json
import jsonpickle

def index(request):
    return HttpResponse("Hello, world.")

def init_state(request):
    env = TextworldEnv().env
    _ , infos = env.reset()
    _ = compute_state([], infos)

    alfworld_env = AlfworldEnv()
    env, agent = alfworld_env.env, alfworld_env.agent

    parser = PDDL_Parser()
    parser.parse_domain(CONSTANTS.FILES.DOMAIN_PDDL_PATH)
    parser.parse_problem(CONSTANTS.FILES.PROBLEM_PDDL_PATH)
    parser.parse_env_infos(infos)
    parser.parse_visible_receptacles(agent)
    parser.parse_distances(agent)
    min_dist_receptacle, max_dist_receptacle = parser.get_distance_info()
    initial_state = InitialState(parser.get_types(),
                                 parser.get_predicates(),
                                 parser.get_atomic_actions(),
                                 parser.get_objects(),
                                 parser.get_locations(),
                                 parser.get_receptacles(),
                                 parser.get_visible_receptacles(),
                                 min_dist_receptacle, max_dist_receptacle)
    return JsonResponse(jsonpickle.dumps(initial_state), safe=False)

@csrf_exempt
def perform_action(request):
    command = request.body.decode('utf-8')
    alfworld_env = AlfworldEnv()
    env, agent = alfworld_env.env, alfworld_env.agent

    error_message, feedback_message = request_check(agent, command)
    if len(error_message) != 0:
        current_state = CurrentState(None, None, None, None, None, error_message, feedback_message)
    else:
        agent.step(command)
        visible_objects, receptacles, current_inventory, current_location, objects_with_updates, error_message, feedback_message = InfoParser().parse(agent, command)
        current_state = CurrentState(visible_objects, receptacles, current_inventory, current_location, objects_with_updates, error_message, feedback_message)
    return JsonResponse(jsonpickle.dumps(current_state), safe=False)

