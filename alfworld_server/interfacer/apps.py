from django.apps import AppConfig
from .alfworld_runner import create_alfworld_env, create_textworld_env
from .alfworld_env import AlfworldEnv, TextworldEnv
from .utils.constants import CONSTANTS

class InterfacerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interfacer'

    def ready(self):
        print("Making things ready")
        _ = TextworldEnv(create_textworld_env())
        env, agent = create_alfworld_env()
        _ = AlfworldEnv(env, agent)