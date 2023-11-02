from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from interfacer.alfworld_runner import create_alfworld_env
from interfacer.alfworld_env import AlfworldEnv
from common.State import State, compute_state
from interfacer.models.InitialState import InitialState
from interfacer.pddl_parser.PDDL import PDDL_Parser
from interfacer.utils.constants import CONSTANTS
import json
import jsonpickle

def index(request):
    return HttpResponse("Hello, world.")

def init_state(request):
    env = AlfworldEnv(create_alfworld_env(CONSTANTS.FILES)).env
    _ , infos = env.reset()
    _ = compute_state([], infos)

    parser = PDDL_Parser()
    parser.parse_domain(CONSTANTS.FILES.DOMAIN_PDDL_PATH)
    parser.parse_problem(CONSTANTS.FILES.PROBLEM_PDDL_PATH)
    parser.parse_env_infos(infos)
    initial_state = InitialState(parser.get_types(),
                                 parser.get_predicates(),
                                 parser.get_atomic_actions(),
                                 parser.get_objects(),
                                 parser.get_locations(),
                                 parser.get_receptacles())
    return JsonResponse(jsonpickle.dumps(initial_state), safe=False)

# def perform_action(request):
#     body = json.loads(request.body.decode('utf-8'))
#     command = body['command']
#     env = AlfworldEnv(create_alfworld_env()).env
#     _ = compute_state([], infos)

