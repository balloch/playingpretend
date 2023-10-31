from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .alfworld_runner import create_alfworld_env
from .alfworld_env import AlfworldEnv
from common.State import State, compute_state
import json

def index(request):
    return HttpResponse("Hello, world.")

def init_state(request):
    env = AlfworldEnv(create_alfworld_env()).env
    _ , infos = env.reset()
    state = compute_state([], infos)
    return JsonResponse(state.toJSON(), safe=False)
