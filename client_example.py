import requests
import jsonpickle
r = requests.get('http://localhost:8000/v1/env')
initial_state = jsonpickle.loads(r.json())

print(initial_state)