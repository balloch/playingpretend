from common.Parameter import Parameter
class Precondition:
    def __init__(self, name, parameters: [Parameter]):
        self.name = name
        self.parameters = parameters

    # def get_variable_names(self, variables:dict):
    #     return [parameter.id for parameter in self.parameters]
    # def check_essential_variables(self, variables: dict):
    #     variable_names = self.get_variable_names(variables)
    #     for variable in self.essential_variables:
    #         if variable not in variable_names:
    #             return False
    #     return True
    #     def evaluate(self, variables: dict) -> bool:
    #         if not self.check_essential_variables(variables):
    #             variable_names = self.get_variable_names(variables)
    #             raise Exception(f"For precondition {self.id}, Insufficient variables: {variable_names}")
    #         return self.eval_fn(variables)
    #
    #
    # PRECONDITIONS = {
    #     ""
    # }
