from interfacer.services.command_checker.InventoryCheck import InventoryCheckBeforeTake, InventoryCheckBeforePut

ALL_CHECKERS = [
    InventoryCheckBeforeTake(),
    InventoryCheckBeforePut()
]

def check(agent, command):
    error_message = "Nothing happens."
    for checker in ALL_CHECKERS:
        if not checker.check(agent, command):
            return error_message, "Check failed at " + checker.name()

    return "",""
