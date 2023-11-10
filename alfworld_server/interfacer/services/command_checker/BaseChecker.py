class BaseChecker:

    def command_valid(self, agent, command):
        raise Exception("Method not implemented")

    def check(self, agent, command):
        # If the command is not valid for this check then simply pass
        command = agent.parse_command(command)
        if not self.command_valid(agent, command):
            return True
        return self.check_condition(agent, command)

    def check_condition(self, agent, command):
        raise Exception("Method not implemented")

    def name(self):
        return "BaseChecker"