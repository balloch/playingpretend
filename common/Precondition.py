class Precondition:
    def __init__(self, name, essential_variables: set, eval_fn):
        self.name = name
        self.essential_variables = essential_variables
        self.eval_fn = eval_fn

    def get_variable_names(self, variables:dict):
        return variables.keys()
    def check_essential_variables(self, variables: dict):
        variable_names = self.get_variable_names(variables)
        for variable in self.essential_variables:
            if variable not in variable_names:
                return False
        return True
    def evaluate(self, variables: dict) -> bool:
        if not self.check_essential_variables(variables):
            variable_names = self.get_variable_names(variables)
            raise Exception(f"For precondition {self.name}, Insufficient variables: {variable_names}")
        return self.eval_fn(variables)


PRECONDITIONS = {
    ""
}
