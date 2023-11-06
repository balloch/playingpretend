import requests
import jsonpickle

def get_initial_state():
    r = requests.get('http://localhost:8000/v1/env')
    return jsonpickle.loads(r.json())

def perform_action(command):
    r = requests.post('http://localhost:8000/v1/action', data=command)
    return jsonpickle.loads(r.json())

print(get_initial_state())
print(perform_action("go to desk 1"))
print(perform_action("take mug 1 from desk 1"))
print(perform_action("put mug 1 in/on desk 1"))

