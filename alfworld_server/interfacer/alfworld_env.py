from interfacer.utils.SingletonMeta import SingletonMeta
class AlfworldEnv(metaclass=SingletonMeta):
    def __init__(self, env=None, agent=None):
        self.env = env
        self.agent = agent

class TextworldEnv(metaclass=SingletonMeta):
    def __init__(self, env=None):
        self.env = env
