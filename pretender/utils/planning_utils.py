from bidict import bidict 


def try_grounding(new_ent, curr_grounding, ent_type='location', curr_loc=None, llm=None):
    """
    given an imaginary location or object, try to ground locations to a real location that is close by in the graph and for objects call the llm to decide which real object is most similar in shape or use
    TODO balloch: implement smart selection
    :param new_obj: the imaginary entity
    :param curr_grounding: the current grounding of the imaginary object
    :param obj_type: the type of object (location or object)
    """
    if new_ent in curr_grounding:
        return curr_grounding[new_ent]
    # Random
    # return random.choice(list(alt_set))
    # Greedy
    for alt,altv in curr_grounding.inverse.items():
        if altv[0:2] == 'r_':
            curr_grounding[new_ent] = alt
            return alt
    return new_ent
