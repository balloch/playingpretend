

def tidy_llm_list_string(llm_list_string, strip_nums=True):
    if type(llm_list_string) is str:
        llm_list = llm_list_string.split('\n')
        if len(llm_list) == 1 and len(llm_list_string.split(',')) > 1:
            print('WARNING: splitting on commas')  # TODO balloch: make this a real warning
            llm_list = llm_list_string.split(',')
    else:
        llm_list = llm_list_string
    if strip_nums:
        return [s.lstrip('0123456789 .').rstrip(' .').strip() for s in llm_list]
    return [s.strip() for s in llm_list]


def grammatical_list_str(ent_list : list, attr=None):
    str_of_ents = ''
    if isinstance(ent_list[0], dict):
        ent_list = [ent[attr] for ent in ent_list]
    # if isinstance(ent_list[0], dict):
    elif type(ent_list[0]).__module__ != "builtins":
        ent_list = [getattr(ent,attr) for ent in ent_list]
    else:
        pass # should only be a list of builtins, classes, or dicts
    for idx, ent in enumerate(ent_list):
        str_of_ents += str(ent)
        if idx != len(ent_list)-1:
            str_of_ents += ', '
        if idx == len(ent_list)-2:
            str_of_ents += 'and '
    return str_of_ents



##########
### Test
##########
if __name__ == '__main__':
    print(grammatical_list_str(['a', 'b']))
    print(grammatical_list_str(['a', 'b', 'c']))
    print(grammatical_list_str(['a', 'b', 'c', 'd']))