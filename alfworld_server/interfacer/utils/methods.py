def get_receptacles_from_agent(agent):
    return [recep['num_id'] for _, recep in agent.receptacles.items()]