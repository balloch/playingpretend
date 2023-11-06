class CustomArgs:
    def __init__(self, problem, controller, debug, load_receps, reward_config):
        self.problem = problem
        self.controller = controller
        self.debug = debug
        self.load_receps = load_receps
        self.reward_config = reward_config