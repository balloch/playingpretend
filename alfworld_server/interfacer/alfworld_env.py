from interfacer.utils.SingletonMeta import SingletonMeta
class AlfworldEnv(metaclass=SingletonMeta):
    def __init__(self, env=None):
        self.env = env
