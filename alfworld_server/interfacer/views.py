from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from interfacer.alfworld_runner import create_alfworld_env
from interfacer.alfworld_env import AlfworldEnv
from common.State import State, compute_state
from interfacer.models.InitialState import InitialState
from interfacer.pddl_parser.PDDL import PDDL_Parser
import json
import jsonpickle

def index(request):
    return HttpResponse("Hello, world.")

def init_state(request):
    # env = AlfworldEnv(create_alfworld_env()).env
    # _ , infos = env.reset()
    # state = compute_state([], infos)
    DOMAIN_PDDL_PATH = "/home/suyash/eilab/playingpretend/alfworld_server/interfacer/data/domain.pddl"
    parser = PDDL_Parser()
    parser.parse_domain(DOMAIN_PDDL_PATH)
    initial_state = InitialState(parser.get_types(), parser.get_predicates(), parser.get_atomic_actions())
    return JsonResponse(jsonpickle.dumps(initial_state), safe=False)
