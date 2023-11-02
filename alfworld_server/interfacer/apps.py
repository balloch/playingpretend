from django.apps import AppConfig
from .alfworld_runner import create_alfworld_env
from .alfworld_env import AlfworldEnv
from .utils.constants import CONSTANTS

class InterfacerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interfacer'

    def ready(self):
        print("Making things ready")
        _ = AlfworldEnv(create_alfworld_env(CONSTANTS.FILES))